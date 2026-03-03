"""Dependency installation for different Linux distributions."""

from __future__ import annotations
from typing import List
from ghostforge.utils.system import run, which, read_os_release


# Common package names (logical names)
COMMON_PKGS = [
    "qemu-img", "qemu-system-x86", "qemu-kvm", "libvirt", "libvirt-daemon",
    "libvirt-clients", "virt-install", "cloud-utils-growpart", "cloud-init",
    "genisoimage", "qemu-nbd", "kpartx"
]

# Package name mappings for different package managers
APT_MAP = {
    "qemu-img": "qemu-utils",
    "qemu-system-x86": "qemu-system-x86",
    "qemu-kvm": "qemu-kvm",
    "libvirt": "libvirt-daemon-system",
    "libvirt-daemon": "libvirt-daemon",
    "libvirt-clients": "libvirt-clients",
    "virt-install": "virtinst",
    "cloud-utils-growpart": "cloud-guest-utils",
    "cloud-init": "cloud-init",
    "genisoimage": "genisoimage",
    "qemu-nbd": "qemu-utils",
    "kpartx": "kpartx",
}

DNF_MAP = {
    "qemu-img": "qemu-img",
    "qemu-system-x86": "qemu-kvm-core",
    "qemu-kvm": "qemu-kvm",
    "libvirt": "libvirt",
    "libvirt-daemon": "libvirt-daemon",
    "libvirt-clients": "libvirt-client",
    "virt-install": "virt-install",
    "cloud-utils-growpart": "cloud-utils-growpart",
    "cloud-init": "cloud-init",
    "genisoimage": "genisoimage",
    "qemu-nbd": "qemu-nbd",
    "kpartx": "kpartx",
}

ZYP_MAP = {
    "qemu-img": "qemu-tools",
    "qemu-system-x86": "qemu-x86",
    "qemu-kvm": "qemu-kvm",
    "libvirt": "libvirt",
    "libvirt-daemon": "libvirt-daemon",
    "libvirt-clients": "libvirt-client",
    "virt-install": "virt-install",
    "cloud-utils-growpart": "cloud-utils",
    "cloud-init": "cloud-init",
    "genisoimage": "genisoimage",
    "qemu-nbd": "qemu-tools",
    "kpartx": "kpartx",
}


def install_deps():
    """Install dependencies based on the detected Linux distribution."""
    osrel = read_os_release()
    id_like = (osrel.get("ID_LIKE", "") + " " + osrel.get("ID", "")).lower()
    
    # Debian/Ubuntu
    if any(x in id_like for x in ["debian", "ubuntu"]):
        print("[deps] Detected Debian/Ubuntu-based system")
        run(["sudo", "apt-get", "update"], check=False)
        pkgs = sorted(set(APT_MAP[p] for p in COMMON_PKGS if p in APT_MAP))
        run(["sudo", "apt-get", "install", "-y"] + pkgs)
    
    # RHEL/Fedora/CentOS/Rocky/AlmaLinux
    elif any(x in id_like for x in ["rhel", "fedora", "centos", "rocky", "almalinux"]):
        pm = "dnf" if which("dnf") else "yum"
        print(f"[deps] Detected RHEL-based system, using {pm}")
        
        if pm == "dnf":
            run(["sudo", "dnf", "-y", "groupinstall", "@virtualization"], check=False)
            pkgs = sorted(set(DNF_MAP[p] for p in COMMON_PKGS if p in DNF_MAP))
            run(["sudo", "dnf", "-y", "install"] + pkgs)
            run(["sudo", "systemctl", "enable", "--now", "libvirtd"], check=False)
        else:
            run(["sudo", "yum", "-y", "groupinstall", "Virtualization Host"], check=False)
            pkgs = sorted(set(DNF_MAP[p] for p in COMMON_PKGS if p in DNF_MAP))
            run(["sudo", "yum", "-y", "install"] + pkgs)
            run(["sudo", "systemctl", "enable", "--now", "libvirtd"], check=False)
    
    # SUSE/openSUSE
    elif any(x in id_like for x in ["suse", "sles", "opensuse"]):
        print("[deps] Detected SUSE-based system")
        run(["sudo", "zypper", "--non-interactive", "refresh"], check=False)
        pkgs = sorted(set(ZYP_MAP[p] for p in COMMON_PKGS if p in ZYP_MAP))
        run(["sudo", "zypper", "--non-interactive", "install"] + pkgs)
        run(["sudo", "systemctl", "enable", "--now", "libvirtd"], check=False)
    
    else:
        print("[deps] Unsupported distro; please install KVM/libvirt/qemu tools manually.")
        return
    
    print("\n[deps] Dependencies installed successfully!")
    print("[deps] If this is your first time, you may need to add your user to 'libvirt' group:")
    print("       sudo usermod -aG libvirt $USER && newgrp libvirt")