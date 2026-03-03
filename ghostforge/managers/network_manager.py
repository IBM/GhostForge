"""Network management for VMs."""

from __future__ import annotations
import tempfile
from pathlib import Path
from typing import Optional
from ghostforge.utils.system import run


class NetworkManager:
    """Manages libvirt networks and NAT configuration."""
    
    def __init__(self):
        """Initialize network manager."""
        pass

    def get_egress_interface(self, probe_ip: str = "8.8.8.8") -> Optional[str]:
        """Detect the host's egress interface by probing a remote IP.
        
        Args:
            probe_ip: IP address to probe for route detection
            
        Returns:
            Name of egress interface or None
        """
        try:
            result = run(["ip", "route", "get", probe_ip], capture_output=True, check=False)
            if result.returncode == 0:
                for part in result.stdout.split():
                    if part == "dev":
                        idx = result.stdout.split().index(part)
                        return result.stdout.split()[idx + 1]
        except Exception:
            pass
        return None

    def ensure_ip_forward(self):
        """Enable IP forwarding on the host."""
        run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"], check=False)
        sysctl_conf = Path("/etc/sysctl.d/99-ipforward.conf")
        if not sysctl_conf.exists():
            try:
                sysctl_conf.write_text("net.ipv4.ip_forward = 1\n", encoding="utf-8")
            except PermissionError:
                print("[network] WARN: Cannot write to /etc/sysctl.d/ (needs sudo)")

    def ensure_libvirt_network(
        self,
        net_name: str,
        bridge_name: str,
        gateway_ip: str,
        netmask: str,
        dhcp_start: str,
        dhcp_end: str,
        recreate: bool = False
    ):
        """Create or ensure a libvirt NAT network exists.
        
        Args:
            net_name: Network name
            bridge_name: Bridge device name
            gateway_ip: Gateway IP address
            netmask: Network mask
            dhcp_start: DHCP range start
            dhcp_end: DHCP range end
            recreate: Whether to recreate the network
        """
        net_xml = f"""<network>
  <name>{net_name}</name>
  <forward mode='nat'/>
  <bridge name='{bridge_name}' stp='on' delay='0'/>
  <ip address='{gateway_ip}' netmask='{netmask}'>
    <dhcp>
      <range start='{dhcp_start}' end='{dhcp_end}'/>
    </dhcp>
  </ip>
</network>"""
        
        # Check if network exists
        net_exists = run(
            ["virsh", "net-info", net_name],
            capture_output=True,
            check=False
        ).returncode == 0
        
        if net_exists and recreate:
            print(f"[network] Recreating network {net_name} (clean config/leases)")
            run(["virsh", "net-destroy", net_name], check=False)
            run(["virsh", "net-undefine", net_name], check=False)
            net_exists = False
        elif net_exists:
            print(f"[network] Network {net_name} already defined")
        
        if not net_exists:
            print(f"[network] Defining network {net_name}")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(net_xml)
                xml_path = f.name
            try:
                run(["virsh", "net-define", xml_path])
            finally:
                Path(xml_path).unlink(missing_ok=True)
        
        # Start and autostart the network
        run(["virsh", "net-start", net_name], check=False)
        run(["virsh", "net-autostart", net_name], check=False)

    def ensure_nat_rules(
        self,
        subnet_cidr: str,
        bridge_name: str,
        egress_if: Optional[str]
    ):
        """Setup iptables NAT rules for the VM network.
        
        Args:
            subnet_cidr: Subnet in CIDR notation
            bridge_name: Bridge device name
            egress_if: Egress interface name
        """
        if not egress_if:
            print("[network] WARN: No egress interface detected, skipping iptables NAT rules")
            return
        
        print(f"[network] Setting up NAT rules: {subnet_cidr} via {egress_if}")
        
        # MASQUERADE rule
        check_cmd = [
            "sudo", "iptables", "-t", "nat", "-C", "POSTROUTING",
            "-s", subnet_cidr, "-o", egress_if, "-j", "MASQUERADE"
        ]
        if run(check_cmd, capture_output=True, check=False).returncode != 0:
            run([
                "sudo", "iptables", "-t", "nat", "-I", "POSTROUTING", "1",
                "-s", subnet_cidr, "-o", egress_if, "-j", "MASQUERADE"
            ])
        
        # FORWARD rules
        check_cmd = [
            "sudo", "iptables", "-C", "FORWARD",
            "-i", bridge_name, "-o", egress_if, "-s", subnet_cidr, "-j", "ACCEPT"
        ]
        if run(check_cmd, capture_output=True, check=False).returncode != 0:
            run([
                "sudo", "iptables", "-I", "FORWARD", "1",
                "-i", bridge_name, "-o", egress_if, "-s", subnet_cidr, "-j", "ACCEPT"
            ])
        
        check_cmd = [
            "sudo", "iptables", "-C", "FORWARD",
            "-i", egress_if, "-o", bridge_name, "-d", subnet_cidr,
            "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"
        ]
        if run(check_cmd, capture_output=True, check=False).returncode != 0:
            run([
                "sudo", "iptables", "-I", "FORWARD", "1",
                "-i", egress_if, "-o", bridge_name, "-d", subnet_cidr,
                "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"
            ])