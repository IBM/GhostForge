# 👻🔨 GhostForge - Phantom VM Automation

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Forge virtual machines from the shadows** - A powerful, modular Python tool to create, manage, and automate VMs using KVM + libvirt.

GhostForge conjures **Ubuntu**, **openSUSE**, and **Windows** VMs with **custom NAT networks**, **cloud-init integration**, and **flexible resource planning**. Like a phantom blacksmith, it forges VMs silently and efficiently.

---

## ✨ Features

- 👻 **Phantom-fast deployment** — Create dozens of VMs in minutes
- 🐧 **Multi-distro support** — Ubuntu/Debian, RHEL/Rocky/Alma, openSUSE/SLES hosts
- 📦 **Automatic dependency installation** via `apt`, `dnf/yum`, or `zypper`
- 🎯 **Image presets** — Official Ubuntu and openSUSE cloud images
- 🪟 **Windows VM support** — SATA disk, e1000e NIC, VNC graphics, autostart
- 🌐 **Custom NAT networks** — Isolated networks with custom subnets, DHCP, and iptables NAT
- ☁️ **Cloud-init integration** — SSH keys, passwords, and automated provisioning (Linux)
- 📊 **Flexible resource allocation** — Fixed percentage or step-based scaling
- 💾 **Storage management** — Overlay-based qcow2 disks on any filesystem
- 🔄 **VM lifecycle management** — Define, start, autostart, and manage VMs
- 🖥️ **VNC support** — Remote desktop access for Windows and Linux VMs
- 🔧 **Modular architecture** — Clean, maintainable, and extensible codebase
---

## ⚠️ Security Notice

**Important:** GhostForge is an automation tool, not a security solution:

- ❌ **No disk encryption** - Does not implement LUKS or dm-crypt
- ⚠️ **Plain text passwords** - Cloud-init passwords stored unencrypted in seed ISOs
- ✅ **Use SSH keys** - Recommended over passwords for authentication
- 🔒 **For encrypted VMs** - Configure LUKS manually after creation using native KVM/QEMU tools

This tool wraps KVM/libvirt for convenience. For enterprise security requirements, use native KVM encryption features.


---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Examples](#-usage-examples)
- [CLI Reference](#-cli-reference)
- [Networking](#-networking)
- [Windows VMs](#-windows-vms)
- [Development](#-development)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔧 Installation

### Prerequisites

- **OS**: Linux with KVM support enabled in BIOS/UEFI
- **Python**: 3.8 or higher
- **Packages**: `qemu-img`, `virt-install`, `virsh`, `libvirt-daemon`, `qemu-kvm`

### Install from PyPI (when published)

```bash
pip install ghostforge
```

### Install from source

```bash
git clone https://github.com/IBM/GhostForge.git
cd GhostForge
pip install -e .
```

### Install dependencies automatically

```bash
sudo ghostforge deps
```

This will detect your distribution and install all required packages.

---

## 🚀 Quick Start

### Forge 5 Ubuntu VMs with step-based resource scaling

```bash
ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/vms \
  --name-prefix ubuntu \
  --count 5 \
  --plan steps --step 20 \
  --image-preset ubuntu-noble \
  --disk-size 40G \
  --cloud-init --ssh-pubkey ~/.ssh/id_rsa.pub \
  --start --headless
```

This forges 5 VMs with:
- VM 1: 20% CPU/RAM
- VM 2: 40% CPU/RAM
- VM 3: 60% CPU/RAM
- VM 4: 80% CPU/RAM
- VM 5: 100% CPU/RAM

### Forge Windows VMs with custom network

```bash
ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/windows \
  --name-prefix win \
  --count 10 \
  --image-path /data/windows-template.qcow2 \
  --windows --vnc --autostart --start \
  --plan fixed --cpu-percent 10 --ram-percent 10 \
  --disk-size 80G \
  --setup-network \
  --network ghostforge-net \
  --subnet-cidr 192.168.150.0/24
```

---

## 📚 Usage Examples

### Linux VMs

#### Ubuntu 24.04 LTS (Noble)
```bash
ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/vms \
  --name-prefix u24 \
  --count 3 \
  --image-preset ubuntu-noble \
  --disk-size 40G \
  --cloud-init --ssh-pubkey ~/.ssh/id_rsa.pub \
  --start
```

#### openSUSE Leap 15.5
```bash
ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/vms \
  --name-prefix leap \
  --count 2 \
  --image-preset opensuse-leap-15.5 \
  --disk-size 60G \
  --cloud-init --ssh-pubkey ~/.ssh/id_rsa.pub \
  --start
```

### Windows VMs

```bash
ghostforge create \
  --base-dir /var/ghostforge \
  --storage-dir /data/windows \
  --name-prefix win \
  --count 5 \
  --image-path /data/win-template.qcow2 \
  --windows --vnc --autostart \
  --plan fixed --cpu-percent 20 --ram-percent 20 \
  --disk-size 80G \
  --start
```

### Custom Network Setup

```bash
ghostforge create \
  --setup-network \
  --network my-net \
  --bridge-name virbr200 \
  --subnet-cidr 192.168.200.0/24 \
  --gateway-ip 192.168.200.1 \
  --dhcp-start 192.168.200.10 \
  --dhcp-end 192.168.200.200 \
  [... other VM options ...]
```

---

## 🛠 CLI Reference

### Commands

- `ghostforge create` — Forge one or more VMs
- `ghostforge mount` — Mount a VM's disk on the host
- `ghostforge unmount` — Unmount a VM's disk
- `ghostforge deps` — Install host dependencies

### Key Options

| Option | Description |
|--------|-------------|
| `--base-dir` | Directory for VM configurations |
| `--storage-dir` | Directory for VM disks |
| `--name-prefix` | Prefix for VM names |
| `--count` | Number of VMs to forge |
| `--image-preset` | OS preset (ubuntu-noble, opensuse-leap-15.5, etc.) |
| `--image-path` | Local image path (for Windows) |
| `--disk-size` | Disk size (e.g., 40G) |
| `--plan` | Resource plan: `fixed` or `steps` |
| `--cloud-init` | Enable cloud-init (Linux only) |
| `--windows` | Forge Windows VMs |
| `--vnc` | Enable VNC graphics |
| `--secure-boot` | Enable UEFI Secure Boot (Windows 11, default: disabled) |
| `--setup-network` | Create custom NAT network |

For full options: `ghostforge create --help`

---

## 🌐 Networking

### Default Network

VMs use libvirt's `default` network by default:
- Bridge: `virbr0`
- Subnet: `192.168.122.0/24`
- DHCP: `192.168.122.2` - `192.168.122.254`

### Custom Networks

Create isolated networks with custom configuration:

```bash
ghostforge create \
  --setup-network \
  --network my-network \
  --bridge-name virbr100 \
  --subnet-cidr 10.0.100.0/24 \
  --gateway-ip 10.0.100.1 \
  --dhcp-start 10.0.100.10 \
  --dhcp-end 10.0.100.200 \
  [... VM options ...]
```

Features:
- Automatic IP forwarding
- iptables NAT rules
- DHCP server
- Egress interface detection

### Find VM IPs

```bash
virsh net-dhcp-leases default
# or
virsh net-dhcp-leases my-network
```

---

## 🪟 Windows VMs

### Requirements
- Pre-configured Windows qcow2 template (golden image)
- Valid Windows license
- For Windows 11: UEFI-enabled golden image with TPM 2.0

### Forging Windows 10 VMs

```bash
ghostforge create \
  --image-path /path/to/windows10-template.qcow2 \
  --windows --vnc --autostart \
  --name-prefix win10 --count 10 \
  --disk-size 80G \
  --start
```

### Forging Windows 11 VMs

Windows 11 requires UEFI boot and TPM 2.0. Use `--os-variant win11`:

```bash
ghostforge create \
  --image-path /path/to/windows11-golden.qcow2 \
  --os-variant win11 \
  --windows --vnc --autostart \
  --name-prefix win11 --count 10 \
  --disk-size 80G \
  --start
```

**Important for Windows 11:**
- Your golden image MUST be created with UEFI boot enabled
- TPM 2.0 is automatically configured when using `--os-variant win11`
- **Secure Boot is DISABLED by default** for compatibility with golden images
- Add `--secure-boot` flag if your golden image requires Secure Boot
- Install virtio drivers in your golden image for better performance (or use SATA)

### Secure Boot Configuration

By default, GhostForge disables UEFI Secure Boot for Windows 11 VMs to ensure compatibility with golden images that aren't signed with Microsoft keys. This prevents "Access Denied" boot errors.

**To enable Secure Boot** (if your golden image requires it):
```bash
ghostforge create \
  --image-path /path/to/windows11-golden.qcow2 \
  --os-variant win11 \
  --windows --vnc --start \
  --secure-boot  # Enable Secure Boot
```

**Verify boot configuration:**
```bash
virsh dumpxml win11-01 | grep -A 5 loader
# Should show: loader.secure='no' (default) or 'yes' (with --secure-boot)
```

### Preparing a Windows 11 Golden Image

1. Create a VM with UEFI and TPM 2.0:
   ```bash
   virt-install --name win11-template \
     --memory 4096 --vcpus 2 \
     --disk size=80 \
     --cdrom /path/to/windows11.iso \
     --os-variant win11 \
     --boot uefi \
     --tpm backend.type=emulator,backend.version=2.0,model=tpm-crb
   ```

2. Install Windows 11 and virtio drivers
3. Configure and sysprep the installation
4. Shut down and use the disk as your golden image

### Accessing via VNC

```bash
# Check VNC port
virsh vncdisplay win11-01

# Connect with VNC client
vncviewer localhost:5900  # for :0
vncviewer HOST:5900       # remote access
```

### Windows-Specific Features
- **Windows 10/Server**: SATA disk, BIOS boot
- **Windows 11**: SATA disk, UEFI boot, TPM 2.0, Secure Boot (optional, disabled by default)
- e1000e network adapter (better compatibility)
- Automatic OVMF firmware detection with fallbacks
- host-model CPU passthrough
- VNC graphics enabled by default
- Autostart support

---

## 👨‍💻 Development

### Setup Development Environment

```bash
git clone https://github.com/IBM/GhostForge.git
cd GhostForge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov=ghostforge --cov-report=html
```

### Code Quality

```bash
# Format code
black ghostforge tests

# Sort imports
isort ghostforge tests

# Lint
flake8 ghostforge tests

# Type check
mypy ghostforge
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with Python and libvirt
- Uses official Ubuntu and openSUSE cloud images
- Inspired by the need for simple, automated VM management

---

## 📞 Support

- 🐛 [Report bugs](https://github.com/IBM/GhostForge/issues)
- 💡 [Request features](https://github.com/IBM/GhostForge/issues)
- 📖 [Documentation](https://github.com/IBM/GhostForge#readme)

---

**Made with ❤️ and 👻 by the GhostForge community**

*"From the shadows, we forge the future of virtualization"*
