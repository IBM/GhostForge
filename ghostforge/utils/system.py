"""System utility functions."""

from __future__ import annotations
import os
import shutil
import subprocess
from typing import List, Optional


def run(cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Execute a command and optionally capture output."""
    print("[cmd]", " ".join(cmd))
    return subprocess.run(cmd, check=check, capture_output=capture_output, text=True)


def which(bin_name: str) -> Optional[str]:
    """Find binary in PATH."""
    return shutil.which(bin_name)


def require_bins(bins: List[str]):
    """Check if required binaries are available."""
    missing = [b for b in bins if not which(b)]
    if missing:
        raise SystemExit(f"Missing required tools: {', '.join(missing)}")


def human_bytes(num_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024 or unit == "TB":
            return f"{num_bytes:.0f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.0f}TB"


def read_os_release() -> dict:
    """Read /etc/os-release file."""
    data = {}
    try:
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v.strip().strip('"')
    except Exception:
        pass
    return data


def total_cpus() -> int:
    """Get total number of CPUs."""
    return os.cpu_count() or 1


def total_mem_bytes() -> int:
    """Get total system memory in bytes."""
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return kb * 1024
    except Exception:
        pass
    return 8 * 1024 ** 3