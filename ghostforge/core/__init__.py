"""Core configuration and data structures."""

from ghostforge.core.config import VMConfig, ResourceShare
from ghostforge.core.presets import PRESETS, get_preset_url

__all__ = [
    "VMConfig",
    "ResourceShare",
    "PRESETS",
    "get_preset_url",
]