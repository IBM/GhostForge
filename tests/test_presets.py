"""Tests for image presets."""

import pytest
from ghostforge.core.presets import PRESETS, get_preset_url


def test_presets_exist():
    """Test that all expected presets are defined."""
    expected_presets = [
        "ubuntu-noble",
        "ubuntu-jammy",
        "opensuse-leap-15.5",
        "opensuse-tumbleweed",
        "windows"
    ]
    
    for preset in expected_presets:
        assert preset in PRESETS


def test_ubuntu_presets():
    """Test Ubuntu preset URLs."""
    assert PRESETS["ubuntu-noble"].startswith("https://cloud-images.ubuntu.com/noble")
    assert PRESETS["ubuntu-jammy"].startswith("https://cloud-images.ubuntu.com/jammy")


def test_opensuse_presets():
    """Test openSUSE preset URLs."""
    assert "opensuse" in PRESETS["opensuse-leap-15.5"].lower()
    assert "opensuse" in PRESETS["opensuse-tumbleweed"].lower()


def test_windows_preset():
    """Test Windows preset (should be None)."""
    assert PRESETS["windows"] is None


def test_get_preset_url():
    """Test get_preset_url function."""
    # Test valid presets
    assert get_preset_url("ubuntu-noble") == PRESETS["ubuntu-noble"]
    assert get_preset_url("UBUNTU-NOBLE") == PRESETS["ubuntu-noble"]  # Case insensitive
    
    # Test invalid preset
    assert get_preset_url("nonexistent") is None
    
    # Test Windows
    assert get_preset_url("windows") is None