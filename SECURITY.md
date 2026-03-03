# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of GhostForge seriously. If you believe you have found a security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub Security Advisories at https://github.com/IBM/GhostForge/security/advisories or contact the IBM Security team. You should receive a response within 48 hours. If for some reason you do not, please follow up to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

This information will help us triage your report more quickly.

## Security Considerations

### ⚠️ Important: No Disk Encryption

**GhostForge does NOT implement disk encryption.** This tool is an automation wrapper around KVM/libvirt and does not provide:
- LUKS encryption
- dm-crypt integration
- Encrypted disk images

If you need encrypted VMs, you must configure LUKS/dm-crypt manually after VM creation using native KVM/QEMU tools.

### VM Isolation

GhostForge creates virtual machines using KVM/libvirt. Please be aware:

- VMs share the host's resources and should be properly isolated
- Network configurations should be reviewed for your security requirements
- VNC access (when enabled) should be properly secured or firewalled
- **Cloud-init passwords are stored in plain text in seed ISOs** - Use SSH keys instead

### Privileged Operations

GhostForge requires elevated privileges for certain operations:

- Creating libvirt networks requires sudo/root access
- Modifying iptables rules requires sudo/root access
- Installing system dependencies requires sudo/root access
- Mounting VM disks requires sudo/root access

Always review commands before running them with elevated privileges.

### SSH Keys

- SSH public keys are embedded in cloud-init configurations
- Ensure you're using the correct SSH keys for your VMs
- Private keys should never be committed to version control
- Use strong SSH key passphrases

### Network Security

- Custom NAT networks expose VMs to the internet through the host
- Review firewall rules and network configurations
- Consider using isolated networks for sensitive workloads
- DHCP leases may contain sensitive information

### Best Practices

1. **Keep software updated**: Regularly update GhostForge, libvirt, and QEMU
2. **Limit access**: Restrict who can create and manage VMs
3. **Monitor resources**: Watch for unusual resource consumption
4. **Secure VNC**: Use SSH tunneling or VPN for VNC access
5. **Review configurations**: Audit VM and network configurations regularly
6. **Use strong passwords**: If using cloud-init passwords, use strong, unique passwords
7. **Backup regularly**: Maintain backups of important VM data

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request.