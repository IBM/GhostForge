"""Tests for configuration data structures."""

import pytest
from pathlib import Path
from ghostforge.core.config import VMConfig, ResourceShare


def test_resource_share():
    """Test ResourceShare dataclass."""
    share = ResourceShare(
        vcpus=4,
        memory_mb=8192,
        percent_cpu=50,
        percent_ram=50
    )
    
    assert share.vcpus == 4
    assert share.memory_mb == 8192
    assert share.percent_cpu == 50
    assert share.percent_ram == 50


def test_vm_config():
    """Test VMConfig dataclass."""
    config = VMConfig(
        name="test-vm",
        vcpus=2,
        memory_mb=4096,
        os_variant="ubuntu24.04",
        network="default",
        disk_path=Path("/tmp/test.qcow2"),
        seed_iso=Path("/tmp/seed.iso"),
        is_windows=False,
        vnc_enabled=False,
        autostart=False
    )
    
    assert config.name == "test-vm"
    assert config.vcpus == 2
    assert config.memory_mb == 4096
    assert config.os_variant == "ubuntu24.04"
    assert config.network == "default"
    assert config.disk_path == Path("/tmp/test.qcow2")
    assert config.seed_iso == Path("/tmp/seed.iso")
    assert config.is_windows is False
    assert config.vnc_enabled is False
    assert config.autostart is False


def test_vm_config_windows():
    """Test VMConfig for Windows VM."""
    config = VMConfig(
        name="win-vm",
        vcpus=4,
        memory_mb=8192,
        os_variant="win2k19",
        network="default",
        disk_path=Path("/tmp/win.qcow2"),
        seed_iso=None,
        is_windows=True,
        vnc_enabled=True,
        autostart=True
    )
    
    assert config.is_windows is True
    assert config.vnc_enabled is True
    assert config.autostart is True
    assert config.seed_iso is None