"""Setup configuration for GhostForge."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="ghostforge",
    version="1.1.0",
    author="GhostForge Contributors",
    author_email="",
    description="GhostForge - Powerful KVM/Libvirt VM Automation Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ghostforge",
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Emulators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - uses only stdlib
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ghostforge=ghostforge.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="kvm libvirt virtualization vm automation cloud-init ghostforge",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/ghostforge/issues",
        "Source": "https://github.com/yourusername/ghostforge",
        "Documentation": "https://github.com/yourusername/ghostforge#readme",
    },
)