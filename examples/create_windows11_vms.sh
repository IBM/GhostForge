#!/bin/bash
# Example: Create Windows 11 VMs with UEFI, TPM 2.0, and custom network
#
# IMPORTANT: Windows 11 requires:
# - UEFI boot (automatically configured when using --os-variant win11)
# - TPM 2.0 (automatically configured when using --os-variant win11)
# - A golden image prepared with Windows 11 installed
#
# NOTE: Secure Boot is DISABLED by default for compatibility with golden images.
# If your golden image requires Secure Boot, add the --secure-boot flag.
#
# To prepare a Windows 11 golden image:
# 1. Install Windows 11 in a VM with UEFI and TPM enabled
# 2. Install virtio drivers for network and storage (or use SATA/e1000e)
# 3. Sysprep the installation (generalize)
# 4. Shut down and export the disk as a qcow2 file

ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/windows11 \
  --name-prefix win11 \
  --count 10 \
  --image-path /data/windows11-golden.qcow2 \
  --os-variant win11 \
  --windows --vnc --autostart --start \
  --plan fixed --cpu-percent 15 --ram-percent 15 \
  --disk-size 80G \
  --setup-network \
  --network ghostforge-net \
  --bridge-name virbr150 \
  --subnet-cidr 192.168.150.0/24 \
  --gateway-ip 192.168.150.1 \
  --dhcp-start 192.168.150.10 \
  --dhcp-end 192.168.150.200
  # Add --secure-boot if your golden image requires Secure Boot

echo "Windows 11 VMs created with UEFI and TPM 2.0!"
echo "Secure Boot: DISABLED (default for compatibility)"
echo ""
echo "Check VNC displays with: virsh vncdisplay <vm-name>"
echo "Get IPs with: virsh net-dhcp-leases ghostforge-net"
echo ""
echo "Verify boot configuration:"
echo "  virsh dumpxml win11-01 | grep -A 5 loader"
echo ""
echo "Note: If VMs don't boot, verify your golden image:"
echo "  - Was created with UEFI boot enabled"
echo "  - Has TPM 2.0 configured"
echo "  - Has SATA controller (or virtio drivers installed)"
echo "  - Was properly sysprepped"