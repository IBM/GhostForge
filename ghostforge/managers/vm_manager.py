"""VM lifecycle management."""

from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple
from ghostforge.core.config import VMConfig
from ghostforge.utils.system import run, require_bins


class VMManager:
    """Manages VM creation and lifecycle."""
    
    # OVMF firmware paths with fallbacks
    OVMF_PATHS = [
        # 4MB OVMF (preferred for modern systems)
        ("/usr/share/OVMF/OVMF_CODE_4M.fd", "/usr/share/OVMF/OVMF_VARS_4M.fd"),
        # Standard OVMF (fallback)
        ("/usr/share/OVMF/OVMF_CODE.fd", "/usr/share/OVMF/OVMF_VARS.fd"),
        # Alternative paths on some distributions
        ("/usr/share/edk2/ovmf/OVMF_CODE.fd", "/usr/share/edk2/ovmf/OVMF_VARS.fd"),
    ]
    
    # Secure Boot OVMF paths (only used when secure_boot=True)
    OVMF_SECUREBOOT_PATHS = [
        ("/usr/share/OVMF/OVMF_CODE_4M.ms.fd", "/usr/share/OVMF/OVMF_VARS_4M.ms.fd"),
        ("/usr/share/OVMF/OVMF_CODE.secboot.fd", "/usr/share/OVMF/OVMF_VARS.ms.fd"),
    ]
    
    def __init__(self, base_dir: Path):
        """Initialize VM manager.
        
        Args:
            base_dir: Base directory for VM configurations
        """
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_ovmf_firmware(self, secure_boot: bool = False) -> Optional[Tuple[str, str]]:
        """Find available OVMF firmware files.
        
        Args:
            secure_boot: Whether to look for Secure Boot enabled firmware
            
        Returns:
            Tuple of (code_path, vars_path) or None if not found
        """
        paths_to_check = self.OVMF_SECUREBOOT_PATHS if secure_boot else self.OVMF_PATHS
        
        for code_path, vars_path in paths_to_check:
            code = Path(code_path)
            vars_file = Path(vars_path)
            if code.exists() and vars_file.exists():
                return (str(code), str(vars_file))
        
        return None

    def vm_dir(self, name: str) -> Path:
        """Get VM directory path.
        
        Args:
            name: VM name
            
        Returns:
            Path to VM directory
        """
        return self.base_dir / name

    def define_and_optionally_start(
        self,
        cfg: VMConfig,
        start: bool,
        graphics: bool
    ):
        """Define a VM and optionally start it.
        
        Args:
            cfg: VM configuration
            start: Whether to start the VM
            graphics: Whether to enable graphics
        """
        require_bins(["virt-install"])
        
        # Base arguments
        args = [
            "virt-install",
            "--name", cfg.name,
            "--memory", str(cfg.memory_mb),
            "--vcpus", str(cfg.vcpus),
            "--import",
            "--noautoconsole",
        ]
        
        # Disk configuration - Windows uses SATA, Linux uses virtio
        if cfg.is_windows:
            args += [
                "--disk",
                f"path={cfg.disk_path},format=qcow2,bus=sata,cache=none,discard=unmap"
            ]
            args += ["--network", f"network={cfg.network},model=e1000e"]
            
            # Windows 11 specific configuration
            if cfg.os_variant and "win11" in cfg.os_variant.lower():
                args += ["--os-variant", cfg.os_variant]
                
                # Find appropriate OVMF firmware
                ovmf = self._find_ovmf_firmware(secure_boot=cfg.secure_boot)
                
                if ovmf:
                    code_path, vars_template = ovmf
                    # Create per-VM NVRAM file path
                    nvram_path = f"/var/lib/libvirt/qemu/nvram/{cfg.name}_VARS.fd"
                    
                    # Manual UEFI configuration without firmware autoselection
                    # This avoids the default Secure Boot with Microsoft keys
                    args += [
                        "--boot",
                        f"loader={code_path},loader.readonly=yes,loader.type=pflash,"
                        f"loader.secure={'yes' if cfg.secure_boot else 'no'},"
                        f"nvram.template={vars_template}"
                    ]
                    
                    print(f"[uefi] Using OVMF firmware: {code_path}")
                    print(f"[uefi] NVRAM template: {vars_template}")
                    print(f"[uefi] Secure Boot: {'enabled' if cfg.secure_boot else 'disabled'}")
                else:
                    # Fallback to simple UEFI if OVMF not found
                    print("[warn] OVMF firmware not found, using virt-install autoselection")
                    args += ["--boot", "uefi"]
                
                # TPM 2.0 required for Windows 11
                args += ["--tpm", "backend.type=emulator,backend.version=2.0,model=tpm-crb"]
                
                # SMM required for UEFI Secure Boot (but we enable it regardless for compatibility)
                args += ["--features", "smm.state=on"]
            elif not cfg.os_variant:
                args += ["--os-variant", "win2k19"]
            else:
                args += ["--os-variant", cfg.os_variant]
            
            args += ["--cpu", "host-model"]
        else:
            args += [
                "--disk",
                f"path={cfg.disk_path},format=qcow2,bus=virtio,discard=unmap,detect_zeroes=unmap"
            ]
            args += ["--network", f"network={cfg.network},model=virtio"]
            if cfg.os_variant:
                args += ["--os-variant", cfg.os_variant]
        
        # Cloud-init seed for Linux
        if cfg.seed_iso:
            args += ["--disk", f"path={cfg.seed_iso},device=cdrom"]
        
        # Graphics configuration
        if cfg.vnc_enabled:
            args += ["--graphics", "vnc,listen=0.0.0.0,port=-1"]
        elif not graphics:
            args += ["--graphics", "none"]
        
        # Start/autostart configuration
        if not start:
            args += ["--noreboot"]
        if cfg.autostart:
            args += ["--autostart"]
        
        run(args)

    def get_vnc_display(self, vm_name: str) -> Optional[str]:
        """Get VNC display port for a VM.
        
        Args:
            vm_name: VM name
            
        Returns:
            VNC display string or None
        """
        result = run(
            ["virsh", "vncdisplay", vm_name],
            capture_output=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None