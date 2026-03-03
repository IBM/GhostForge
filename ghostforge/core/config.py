"""Configuration data structures."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ResourceShare:
    """Resource allocation for a VM."""
    vcpus: int
    memory_mb: int
    percent_cpu: int
    percent_ram: int


@dataclass
class VMConfig:
    """VM configuration."""
    name: str
    vcpus: int
    memory_mb: int
    os_variant: Optional[str]
    network: str
    disk_path: Path
    seed_iso: Optional[Path]
    is_windows: bool = False
    vnc_enabled: bool = False
    autostart: bool = False
    secure_boot: bool = False