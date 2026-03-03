#!/bin/bash
# Example: Create 5 Ubuntu VMs with step-based resource allocation

ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/vms \
  --name-prefix ubuntu \
  --count 5 \
  --plan steps --step 20 \
  --image-preset ubuntu-noble \
  --disk-size 40G \
  --network default \
  --os-variant ubuntu24.04 \
  --cloud-init --ssh-pubkey ~/.ssh/id_rsa.pub \
  --start --headless

echo "VMs created! Check status with: virsh list --all"
echo "Get IPs with: virsh net-dhcp-leases default"