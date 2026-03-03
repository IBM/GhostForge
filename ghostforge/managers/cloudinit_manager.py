"""Cloud-init seed generation for Linux VMs."""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from ghostforge.utils.system import run, which


class CloudInitManager:
    """Manages cloud-init seed creation."""
    
    def __init__(self, cache_dir: Path):
        """Initialize cloud-init manager.
        
        Args:
            cache_dir: Directory to cache cloud-init seeds
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def create_seed(
        self,
        vm_dir: Path,
        hostname: str,
        ssh_pubkey: Optional[str],
        password: Optional[str]
    ) -> Optional[Path]:
        """Create a cloud-init seed ISO.
        
        Args:
            vm_dir: VM directory
            hostname: VM hostname
            ssh_pubkey: SSH public key content
            password: Root password (optional)
            
        Returns:
            Path to seed ISO or None if tools not available
        """
        user_data = ["#cloud-config", f"hostname: {hostname}"]
        
        if ssh_pubkey:
            user_data += ["ssh_authorized_keys:", f"  - {ssh_pubkey.strip()}"]
        
        if password:
            user_data += [
                "chpasswd:",
                "  list: |",
                f"    root:{password}",
                "  expire: False",
                "ssh_pwauth: True",
            ]
        
        user_data_str = "\n".join(user_data) + "\n"
        meta_data_str = f"instance-id: {hostname}\nlocal-hostname: {hostname}\n"
        
        seed_dir = vm_dir / "seed"
        seed_dir.mkdir(parents=True, exist_ok=True)
        (seed_dir / "user-data").write_text(user_data_str, encoding="utf-8")
        (seed_dir / "meta-data").write_text(meta_data_str, encoding="utf-8")

        seed_iso = vm_dir / "seed.iso"
        
        # Try cloud-localds first
        if which("cloud-localds"):
            run([
                "cloud-localds",
                str(seed_iso),
                str(seed_dir / "user-data"),
                str(seed_dir / "meta-data")
            ])
            return seed_iso
        
        # Fall back to mkisofs/genisoimage
        mkisofs = which("mkisofs") or which("genisoimage")
        if mkisofs:
            run([
                mkisofs,
                "-output", str(seed_iso),
                "-volid", "cidata",
                "-joliet",
                "-rock",
                str(seed_dir)
            ])
            return seed_iso
        
        print("[cloud-init] cloud-localds/mkisofs not found; proceeding without cloud-init seed")
        return None