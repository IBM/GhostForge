"""Resource planning and allocation utilities."""

from __future__ import annotations
import math
from typing import List
from ghostforge.core.config import ResourceShare
from ghostforge.utils.system import total_cpus, total_mem_bytes


def clamp(n: int, lo: int, hi: int) -> int:
    """Clamp a value between min and max."""
    return max(lo, min(n, hi))


def plan_steps(count: int, step: int) -> List[int]:
    """Generate step-based resource percentages."""
    out = []
    p = step
    for _ in range(count):
        out.append(clamp(p, 1, 100))
        p = min(p + step, 100)
    return out


def compute_resources(count: int, cpu_percents: List[int], ram_percents: List[int]) -> List[ResourceShare]:
    """Compute resource allocation for VMs."""
    cpus = total_cpus()
    mem_bytes = total_mem_bytes()
    shares: List[ResourceShare] = []
    
    for i in range(count):
        cpu_pct = clamp(cpu_percents[i], 1, 100)
        ram_pct = clamp(ram_percents[i], 1, 100)
        vcpus = max(1, math.floor(cpus * cpu_pct / 100))
        mem_mb = max(256, math.floor((mem_bytes / (1024 * 1024)) * ram_pct / 100))
        shares.append(
            ResourceShare(
                vcpus=vcpus,
                memory_mb=mem_mb,
                percent_cpu=cpu_pct,
                percent_ram=ram_pct
            )
        )
    
    return shares