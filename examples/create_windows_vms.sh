#!/bin/bash
# Example: Create 30 Windows VMs with custom network

ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/windows \
  --name-prefix win \
  --count 30 \
  --image-path /data/windows-template.qcow2 \
  --windows --vnc --autostart --start \
  --plan fixed --cpu-percent 10 --ram-percent 10 \
  --disk-size 80G \
  --setup-network \
  --network ghostforge-net \
  --bridge-name virbr150 \
  --subnet-cidr 192.168.150.0/24 \
  --gateway-ip 192.168.150.1 \
  --dhcp-start 192.168.150.10 \
  --dhcp-end 192.168.150.200

echo "Windows VMs created!"
echo "Check VNC displays with: virsh vncdisplay <vm-name>"
echo "Get IPs with: virsh net-dhcp-leases ghostforge-net"