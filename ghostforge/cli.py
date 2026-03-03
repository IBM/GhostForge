"""Command-line interface for VMFarm."""

from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Optional

from ghostforge.core.config import VMConfig
from ghostforge.core.presets import PRESETS
from ghostforge.managers import (
    ImageManager,
    DiskManager,
    CloudInitManager,
    NetworkManager,
    VMManager,
    MountManager,
    install_deps,
)
from ghostforge.utils.resources import plan_steps, compute_resources


def cmd_create(args: argparse.Namespace):
    """Create VMs based on arguments."""
    if args.install_deps:
        install_deps()

    base_dir = Path(args.base_dir).expanduser().resolve()
    storage_dir = Path(args.storage_dir).expanduser().resolve()
    images_dir = base_dir / "images"

    # Setup custom network if requested
    if args.setup_network:
        net_mgr = NetworkManager()
        print(f"[network] Setting up custom network: {args.network}")
        net_mgr.ensure_ip_forward()
        net_mgr.ensure_libvirt_network(
            args.network,
            args.bridge_name,
            args.gateway_ip,
            args.netmask,
            args.dhcp_start,
            args.dhcp_end,
            args.recreate_network
        )
        egress_if = net_mgr.get_egress_interface(args.probe_ip)
        net_mgr.ensure_nat_rules(args.subnet_cidr, args.bridge_name, egress_if)

    img_mgr = ImageManager(images_dir)
    disk_mgr = DiskManager(storage_dir)
    vm_mgr = VMManager(base_dir)
    ci_mgr = CloudInitManager(base_dir / "seed-cache")

    # Determine if this is a Windows VM
    is_windows = args.image_preset == "windows" or (
        args.windows if hasattr(args, 'windows') else False
    )

    base_image = img_mgr.obtain_image(
        args.image_url,
        Path(args.image_path) if args.image_path else None,
        args.image_checksum,
        args.image_checksum_algo,
        args.image_preset,
    )

    count = args.count
    if args.plan == "steps":
        percents = plan_steps(count, args.step)
        cpu_percents = percents
        ram_percents = percents
    else:
        cpu_percents = [args.cpu_percent] * count
        ram_percents = [args.ram_percent] * count

    shares = compute_resources(count, cpu_percents, ram_percents)

    created = []
    vnc_displays = []
    
    for idx in range(count):
        name = f"{args.name_prefix}-{idx+1:02d}"
        vm_dir = vm_mgr.vm_dir(name)
        overlay = disk_mgr.create_overlay(base_image, vm_dir, args.disk_size)
        
        # Cloud-init only for Linux VMs
        ssh_key = None
        seed_iso = None
        if not is_windows and args.cloud_init:
            if args.ssh_pubkey:
                ssh_path = Path(args.ssh_pubkey).expanduser()
                if ssh_path.exists():
                    ssh_key = ssh_path.read_text(encoding="utf-8").strip()
                else:
                    print(f"[warn] SSH public key not found: {ssh_path}")
            seed_iso = ci_mgr.create_seed(vm_dir, name, ssh_key, args.password)

        cfg = VMConfig(
            name=name,
            vcpus=shares[idx].vcpus,
            memory_mb=shares[idx].memory_mb,
            os_variant=args.os_variant,
            network=args.network,
            disk_path=overlay,
            seed_iso=seed_iso,
            is_windows=is_windows,
            vnc_enabled=args.vnc if hasattr(args, 'vnc') else False,
            autostart=args.autostart if hasattr(args, 'autostart') else False,
            secure_boot=args.secure_boot if hasattr(args, 'secure_boot') else False,
        )

        print(
            f"\n[plan] {name}: vCPUs={cfg.vcpus} ({shares[idx].percent_cpu}%), "
            f"RAM={cfg.memory_mb}MB ({shares[idx].percent_ram}%), disk={overlay}"
        )
        
        if not args.dry_run:
            vm_mgr.define_and_optionally_start(cfg, start=args.start, graphics=not args.headless)
            if cfg.vnc_enabled and args.start:
                vnc = vm_mgr.get_vnc_display(name)
                if vnc:
                    vnc_displays.append((name, vnc))
        created.append((name, vm_dir, overlay))

    print("\n[summary]")
    for (name, vm_dir, overlay) in created:
        print(f"- {name} -> dir={vm_dir} disk={overlay}")
    
    if vnc_displays:
        print("\n[VNC displays]")
        for name, vnc in vnc_displays:
            print(f"  {name}: {vnc}")
    
    if args.start and not args.dry_run:
        if is_windows or (hasattr(args, 'vnc') and args.vnc):
            print("\nUse 'virsh list --all' to see VMs. Connect via VNC to the displays shown above.")
        else:
            print("\nUse 'virsh list --all' to see VMs. Connect with: virsh console <name>")
        
        if args.setup_network:
            print(f"\nTo see DHCP leases: virsh net-dhcp-leases {args.network}")


def cmd_mount(args: argparse.Namespace):
    """Mount a VM disk."""
    vm_dir = Path(args.vm_dir).expanduser().resolve()
    mm = MountManager()
    mnt = mm.mount_vm_disk(vm_dir)
    print(f"To unmount: ghostforge unmount --vm-dir {vm_dir}")


def cmd_unmount(args: argparse.Namespace):
    """Unmount a VM disk."""
    vm_dir = Path(args.vm_dir).expanduser().resolve()
    mm = MountManager()
    mm.unmount_vm_disk(vm_dir)


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    p = argparse.ArgumentParser(
        description="VMFarm - KVM/libvirt VM automation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # Create command
    pc = sub.add_parser("create", help="Create one or more VMs")
    pc.add_argument(
        "--install-deps",
        action="store_true",
        help="Install KVM/libvirt/qemu dependencies before creating VMs"
    )
    pc.add_argument("--base-dir", required=True, help="Directory to store VM definitions")
    pc.add_argument("--storage-dir", required=True, help="Directory for VM disks")
    pc.add_argument("--name-prefix", required=True, help="Prefix for VM names")
    pc.add_argument("--count", type=int, default=1, help="Number of VMs to create")

    # Image options
    pc.add_argument(
        "--image-preset",
        choices=sorted(PRESETS.keys()),
        help="OS image preset to download"
    )
    pc.add_argument("--image-url", help="URL to base QCOW2/RAW image")
    pc.add_argument("--image-path", help="Local path to base image")
    pc.add_argument("--image-checksum", help="Optional checksum for verification")
    pc.add_argument(
        "--image-checksum-algo",
        choices=["md5", "sha1", "sha256", "sha512"],
        help="Checksum algorithm"
    )

    # Disk options
    pc.add_argument("--disk-size", default="40G", help="Overlay disk size (e.g., 40G)")

    # Resource planning
    pc.add_argument(
        "--plan",
        choices=["fixed", "steps"],
        default="steps",
        help="Resource allocation plan"
    )
    pc.add_argument("--step", type=int, default=20, help="Step percent when plan=steps")
    pc.add_argument("--cpu-percent", type=int, default=20, help="Fixed CPU percent per VM")
    pc.add_argument("--ram-percent", type=int, default=20, help="Fixed RAM percent per VM")

    # VM options
    pc.add_argument("--os-variant", default=None, help="osinfo variant")
    pc.add_argument("--network", default="default", help="libvirt network name")
    pc.add_argument(
        "--cloud-init",
        action="store_true",
        help="Create cloud-init seed (Linux only)"
    )
    pc.add_argument(
        "--ssh-pubkey",
        default=str(Path.home() / ".ssh/id_rsa.pub"),
        help="SSH public key for cloud-init"
    )
    pc.add_argument("--password", default=None, help="Root password for cloud-init")
    pc.add_argument("--start", action="store_true", help="Start VMs after creation")
    pc.add_argument("--headless", action="store_true", help="Use --graphics none")

    # Windows-specific options
    pc.add_argument("--windows", action="store_true", help="Create Windows VMs")
    pc.add_argument("--vnc", action="store_true", help="Enable VNC graphics")
    pc.add_argument("--autostart", action="store_true", help="Set VMs to autostart")
    pc.add_argument(
        "--secure-boot",
        action="store_true",
        help="Enable UEFI Secure Boot (Windows 11 only, default: disabled for compatibility)"
    )

    # Network options
    pc.add_argument(
        "--setup-network",
        action="store_true",
        help="Create/configure custom libvirt NAT network"
    )
    pc.add_argument("--bridge-name", default="virbr150", help="Bridge name")
    pc.add_argument("--subnet-cidr", default="192.168.150.0/24", help="Subnet CIDR")
    pc.add_argument("--gateway-ip", default="192.168.150.1", help="Gateway IP")
    pc.add_argument("--netmask", default="255.255.255.0", help="Netmask")
    pc.add_argument("--dhcp-start", default="192.168.150.10", help="DHCP range start")
    pc.add_argument("--dhcp-end", default="192.168.150.200", help="DHCP range end")
    pc.add_argument("--probe-ip", default="8.8.8.8", help="IP for egress detection")
    pc.add_argument(
        "--recreate-network",
        action="store_true",
        help="Destroy and recreate network"
    )

    pc.add_argument("--dry-run", action="store_true", help="Plan only, don't create")

    # Mount command
    pm = sub.add_parser("mount", help="Mount a VM's qcow2 on the host")
    pm.add_argument("--vm-dir", required=True, help="Path to VM directory")

    # Unmount command
    pu = sub.add_parser("unmount", help="Unmount a previously mounted VM qcow2")
    pu.add_argument("--vm-dir", required=True, help="Path to VM directory")

    # Deps command
    sub.add_parser("deps", help="Install host dependencies")

    return p


def main(argv: Optional[List[str]] = None):
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.cmd == "create":
        cmd_create(args)
    elif args.cmd == "mount":
        cmd_mount(args)
    elif args.cmd == "unmount":
        cmd_unmount(args)
    elif args.cmd == "deps":
        install_deps()
    else:
        parser.error("Unknown command")


if __name__ == "__main__":
    main()