"""
GhostForge - KVM/Libvirt VM Automation Tool

A powerful, modular Python tool to create, manage, and automate virtual machines
using KVM + libvirt with support for Ubuntu, openSUSE, and Windows VMs.
"""

__version__ = "1.0.0"
__author__ = "GhostForge Contributors"
__license__ = "Apache-2.0"

from ghostforge.core.config import VMConfig, ResourceShare
from ghostforge.managers.vm_manager import VMManager
from ghostforge.managers.image_manager import ImageManager
from ghostforge.managers.disk_manager import DiskManager
from ghostforge.managers.network_manager import NetworkManager
from ghostforge.managers.cloudinit_manager import CloudInitManager

__all__ = [
    "VMConfig",
    "ResourceShare",
    "VMManager",
    "ImageManager",
    "DiskManager",
    "NetworkManager",
    "CloudInitManager",
    "__version__",
]