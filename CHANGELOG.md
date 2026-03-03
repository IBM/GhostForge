# Changelog

All notable changes to GhostForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-17

### Added
- Initial release of GhostForge
- Multi-distribution support (Ubuntu, openSUSE, Windows)
- Automatic dependency installation for Ubuntu/Debian, RHEL/Rocky/Alma, and openSUSE/SLES
- Image presets for Ubuntu Noble, Ubuntu Jammy, openSUSE Leap 15.5, and openSUSE Tumbleweed
- Windows VM support with SATA disk, e1000e NIC, and VNC graphics
- Custom NAT network creation with configurable subnets and DHCP ranges
- Cloud-init integration for Linux VMs (SSH keys, passwords, hostname)
- Flexible resource allocation (fixed percentage or step-based scaling)
- Storage management with overlay-based qcow2 disks
- VM lifecycle management (define, start, autostart)
- Optional disk mounting via qemu-nbd
- VNC support for remote desktop access
- Modular architecture with separate managers for images, disks, networks, cloud-init, and VMs
- Comprehensive CLI with create, mount, unmount, and deps commands
- Full documentation with examples and troubleshooting guide

### Features
- **Image Management**: Download and cache cloud images with checksum verification
- **Disk Management**: Create overlay disks with custom sizes on specified storage
- **Network Management**: Create isolated NAT networks with automatic iptables rules
- **Cloud-init**: Automated VM provisioning with SSH keys and passwords
- **Resource Planning**: Allocate CPU/RAM by percentage with fixed or step-based plans
- **Windows Support**: Optimized settings for Windows VMs
- **Mount Support**: Mount VM disks on host for inspection/modification

### Documentation
- Comprehensive README with installation, usage, and examples
- Contributing guidelines
- MIT License
- Changelog

## [Unreleased]

### Planned
- Additional OS presets (Fedora, Debian, CentOS Stream)
- Snapshot management
- VM cloning
- Batch operations
- Web UI (optional)
- Ansible integration
- Terraform provider

## [1.1.0] - 2026-02-24

### Added
- **Windows 11 Support**: Full support for Windows 11 VMs with automatic UEFI and TPM 2.0 configuration
  - Automatic UEFI boot configuration when using `--os-variant win11`
  - Automatic TPM 2.0 emulator setup (backend.type=emulator, backend.version=2.0, model=tpm-crb)
  - Automatic Secure Boot enablement via SMM (System Management Mode)
  - New `windows11` preset in image presets
- **Documentation**: Comprehensive Windows 11 setup guide and troubleshooting documentation
  - New `WINDOWS11_TROUBLESHOOTING.md` with bilingual (English/Spanish) troubleshooting guide
  - Updated README.md with Windows 11 specific instructions
  - Step-by-step golden image creation guide
  - Common issues and solutions
- **Examples**: New `examples/create_windows11_vms.sh` script with best practices

### Changed
- Enhanced VM manager to detect Windows 11 via `os_variant` parameter
- Updated Windows VM configuration logic to support both Windows 10 (BIOS) and Windows 11 (UEFI)
- Improved documentation for Windows VM requirements and setup

### Technical Details
- Windows 10/Server VMs continue to use BIOS boot (backward compatible)
- Windows 11 VMs automatically configured with:
  - `--boot uefi` for UEFI firmware
  - `--tpm backend.type=emulator,backend.version=2.0,model=tpm-crb` for TPM 2.0
  - `--features smm.state=on` for Secure Boot support
- SATA disk controller and e1000e network adapter maintained for compatibility

### Requirements
- Host must have `swtpm` and `swtpm-tools` installed for TPM emulation
- Host must have OVMF (UEFI firmware) installed
- Golden image must be created with UEFI boot enabled
- Minimum 4GB RAM and 64GB disk recommended for Windows 11 VMs

---

## Version History

- **1.0.0** (2026-02-17): Initial release with core functionality