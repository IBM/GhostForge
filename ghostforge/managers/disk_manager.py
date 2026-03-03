"""Disk management for VMs."""

from __future__ import annotations
from pathlib import Path
from ghostforge.utils.system import run, require_bins


class DiskManager:
    """Manages VM disk creation and storage."""
    
    def __init__(self, storage_dir: Path):
        """Initialize disk manager.
        
        Args:
            storage_dir: Directory to store VM disks
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def create_overlay(self, base_image: Path, vm_dir: Path, disk_size: str) -> Path:
        """Create an overlay disk for a VM.
        
        Args:
            base_image: Path to base image
            vm_dir: VM directory
            disk_size: Disk size (e.g., "40G")
            
        Returns:
            Path to the created overlay disk
        """
        vm_dir.mkdir(parents=True, exist_ok=True)
        overlay = vm_dir / "disk.qcow2"
        on_storage = self.storage_dir / vm_dir.name
        on_storage.mkdir(parents=True, exist_ok=True)
        overlay_on_storage = on_storage / overlay.name
        
        require_bins(["qemu-img"])
        run([
            "qemu-img", "create",
            "-f", "qcow2",
            "-F", "qcow2",
            "-b", str(base_image),
            str(overlay_on_storage),
            disk_size
        ])
        
        if not overlay.exists():
            overlay.symlink_to(overlay_on_storage)
        
        return overlay_on_storage