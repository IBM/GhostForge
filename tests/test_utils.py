"""Tests for utility functions."""

import pytest
from ghostforge.utils.system import human_bytes
from ghostforge.utils.resources import clamp, plan_steps, compute_resources


def test_human_bytes():
    """Test human-readable byte conversion."""
    assert human_bytes(0) == "0B"
    assert human_bytes(1023) == "1023B"
    assert human_bytes(1024) == "1KB"
    assert human_bytes(1024 * 1024) == "1MB"
    assert human_bytes(1024 * 1024 * 1024) == "1GB"
    assert human_bytes(1024 * 1024 * 1024 * 1024) == "1TB"


def test_clamp():
    """Test value clamping."""
    from ghostforge.utils.resources import clamp
    
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
    assert clamp(10, 0, 10) == 10
    assert clamp(0, 0, 10) == 0


def test_plan_steps():
    """Test step-based resource planning."""
    # Test basic step plan
    result = plan_steps(5, 20)
    assert result == [20, 40, 60, 80, 100]
    
    # Test with larger step
    result = plan_steps(3, 50)
    assert result == [50, 100, 100]
    
    # Test with small step
    result = plan_steps(10, 10)
    assert result == [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def test_compute_resources():
    """Test resource computation."""
    # Test fixed allocation
    cpu_percents = [20, 20, 20]
    ram_percents = [20, 20, 20]
    
    shares = compute_resources(3, cpu_percents, ram_percents)
    
    assert len(shares) == 3
    for share in shares:
        assert share.vcpus >= 1
        assert share.memory_mb >= 256
        assert share.percent_cpu == 20
        assert share.percent_ram == 20


def test_compute_resources_steps():
    """Test resource computation with steps."""
    cpu_percents = [20, 40, 60]
    ram_percents = [20, 40, 60]
    
    shares = compute_resources(3, cpu_percents, ram_percents)
    
    assert len(shares) == 3
    assert shares[0].percent_cpu == 20
    assert shares[1].percent_cpu == 40
    assert shares[2].percent_cpu == 60
    assert shares[0].percent_ram == 20
    assert shares[1].percent_ram == 40
    assert shares[2].percent_ram == 60