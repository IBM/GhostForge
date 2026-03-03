"""Image presets for common distributions."""

from typing import Optional

# Official cloud image URLs
UBUNTU_NOBLE_URL = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img"
UBUNTU_JAMMY_URL = "https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img"
OPENSUSE_LEAP155_URL = "https://cdn.opensuse.org/distribution/leap/15.5/appliances/openSUSE-Leap-15.5-Minimal-VM.x86_64-Cloud.qcow2"
OPENSUSE_TW_MINIMAL_URL = "https://download.opensuse.org/tumbleweed/appliances/openSUSE-Tumbleweed-Minimal-VM.x86_64-Cloud.qcow2"

PRESETS = {
    "ubuntu-noble": UBUNTU_NOBLE_URL,
    "ubuntu-jammy": UBUNTU_JAMMY_URL,
    "opensuse-leap-15.5": OPENSUSE_LEAP155_URL,
    "opensuse-tumbleweed": OPENSUSE_TW_MINIMAL_URL,
    "windows": None,  # Windows requires local image path
    "windows11": None,  # Windows 11 requires local image path (use with --os-variant win11)
}


def get_preset_url(preset: str) -> Optional[str]:
    """Get URL for a preset image."""
    return PRESETS.get(preset.lower())