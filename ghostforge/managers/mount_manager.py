"""Disk mounting utilities."""

from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import List, Optional, Tuple
from ghostforge.utils.system import run, require_bins


class MountManager:
    """Manages mounting/unmounting of qcow2 disks."""
    
    def __init__(self):
        """Initialize mount manager."""
        pass

    def mount_qcow2(
        self,
        qcow2: Path,
        mount_point: Path
    ) -> Tuple[Optional[str], Optional[List[str]]]:
        """Mount a qcow2 disk image.
        
        Args:
            qcow2: Path to qcow2 file
            mount_point: Where to mount
            
        Returns:
            Tuple of (nbd_device, mapped_partitions)
        """
        require_bins(["qemu-nbd", "kpartx", "mount"])
        mount_point.mkdir(parents=True, exist_ok=True)
        
        nbd_dev = None
        for i in range(0, 32):
            cand = f"/dev/nbd{i}"
            if not os.path.exists(cand):
                continue
            try:
                run(["qemu-nbd", "-c", cand, str(qcow2)])
                nbd_dev = cand
                break
            except Exception:
                continue
        
        if not nbd_dev:
            raise SystemExit("No free /dev/nbdX device found")
        
        run(["kpartx", "-a", nbd_dev])
        time.sleep(1)
        
        parts = sorted([
            p for p in os.listdir("/dev/mapper")
            if p.startswith(os.path.basename(nbd_dev).replace("/", "") + "p")
        ])
        
        if not parts:
            print("[mount] No partitions detected; attempting to mount whole device")
            run(["mount", nbd_dev, str(mount_point)])
            return nbd_dev, []
        
        first = "/dev/mapper/" + parts[0]
        run(["mount", first, str(mount_point)])
        return nbd_dev, ["/dev/mapper/" + p for p in parts]

    def unmount_qcow2(
        self,
        mount_point: Path,
        nbd_dev: str,
        mapped_parts: List[str]
    ):
        """Unmount a qcow2 disk image.
        
        Args:
            mount_point: Mount point to unmount
            nbd_dev: NBD device to disconnect
            mapped_parts: Mapped partitions to clean up
        """
        try:
            run(["umount", str(mount_point)], check=False)
        finally:
            if mapped_parts:
                run(["kpartx", "-d", nbd_dev], check=False)
            run(["qemu-nbd", "-d", nbd_dev], check=False)

    def mount_vm_disk(self, vm_dir: Path) -> Path:
        """Mount a VM's disk and return mount point.
        
        Args:
            vm_dir: VM directory
            
        Returns:
            Path to mount point
        """
        qcow2 = vm_dir / "disk.qcow2"
        if not qcow2.exists():
            links = list(vm_dir.glob("*.qcow2"))
            if links:
                qcow2 = links[0]
        
        if not qcow2.exists():
            raise SystemExit(f"QCOW2 not found in {vm_dir}")
        
        mnt = vm_dir / "mnt"
        nbd, parts = self.mount_qcow2(qcow2, mnt)
        
        if nbd:
            lock = vm_dir / ".mount.json"
            lock.write_text(
                json.dumps({
                    "nbd": nbd,
                    "parts": parts,
                    "mount_point": str(mnt)
                }),
                encoding="utf-8"
            )
            print(f"Mounted at {mnt}")
        
        return mnt

    def unmount_vm_disk(self, vm_dir: Path):
        """Unmount a VM's disk.
        
        Args:
            vm_dir: VM directory
        """
        lock = vm_dir / ".mount.json"
        if not lock.exists():
            raise SystemExit("No mount lock found; nothing to unmount")
        
        info = json.loads(lock.read_text(encoding="utf-8"))
        self.unmount_qcow2(
            Path(info["mount_point"]),
            info["nbd"],
            info.get("parts") or []
        )
        
        try:
            lock.unlink()
        except Exception:
            pass
        
        print("Unmounted.")