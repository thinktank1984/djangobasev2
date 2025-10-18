# Setup Scripts

This directory contains installation and setup scripts for the DjangoBaseV2 project.

## Available Scripts

### OpenSpec Installation (`openspec_install.sh`)

A comprehensive installation script for OpenSpec, a tool for generating API specifications from code.

#### Features

- **Prerequisites Checking**: Automatically checks for Node.js and npm
- **Automatic Installation**: Installs Node.js if not present (supports multiple platforms)
- **Version Verification**: Ensures Node.js version meets requirements (>= 16.0.0)
- **Update Management**: Handles existing installations with update prompts
- **Cross-Platform Support**: Works on Linux, macOS, and supports various package managers
- **Error Handling**: Robust error handling with detailed logging
- **Verification**: Post-installation verification and functionality testing

#### Usage

```bash
# Install OpenSpec
./openspec_install.sh

# Show help
./openspec_install.sh --help

# Show script version
./openspec_install.sh --version

# Uninstall OpenSpec
./openspec_install.sh --uninstall
```

#### Supported Platforms

- **Linux**:
  - Debian/Ubuntu (apt)
  - CentOS/RHEL (yum)
  - Fedora (dnf)
- **macOS**: Homebrew

#### Prerequisites

- **System**: Linux, macOS, or Windows (with WSL)
- **Permissions**: May require sudo for global npm installation
- **Network**: Internet connection for downloading packages

#### What Gets Installed

- **Node.js**: LTS version (if not present)
- **npm**: Node Package Manager (comes with Node.js)
- **OpenSpec**: Latest version via `@fission-ai/openspec` npm package

#### Installation Process

1. **Prerequisites Check**: Verifies Node.js >= 16.0.0 and npm are installed
2. **Auto-install Node.js**: If missing, attempts to install based on platform detection
3. **OpenSpec Installation**: Installs or updates OpenSpec globally
4. **Verification**: Tests that OpenSpec is working correctly
5. **Usage Guidance**: Displays helpful information for getting started

#### Example Output

```
[2024-01-15 10:30:15] Starting OpenSpec installation...
[2024-01-15 10:30:15] Checking prerequisites...
[2024-01-15 10:30:15] ✓ Node.js version 18.17.0 meets requirements (>= 16.0.0)
[2024-01-15 10:30:15] ✓ npm version 9.6.7 found
[2024-01-15 10:30:15] Installing OpenSpec globally...
[2024-01-15 10:30:45] ✓ OpenSpec installed successfully
[2024-01-15 10:30:45] Verifying OpenSpec installation...
[2024-01-15 10:30:45] ✓ OpenSpec is installed (version: 2.1.0)
[2024-01-15 10:30:45] Testing OpenSpec functionality...
[2024-01-15 10:30:45] ✓ OpenSpec is working correctly

[2024-01-15 10:30:45] ✓ OpenSpec installation completed successfully!

Usage:
  openspec --help          Show help information
  openspec --version       Show version information
  openspec init            Initialize a new OpenSpec project
  openspec generate        Generate specifications from code
  openspec validate        Validate specifications

For more information, visit: https://github.com/fission-ai/openspec
```

## Adding New Scripts

When adding new setup scripts to this directory, please:

1. **Make them executable**: `chmod +x script_name.sh`
2. **Include help functionality**: Add `--help` and `--version` options
3. **Add proper error handling**: Use `set -e` and comprehensive error checking
4. **Include logging**: Add timestamped log messages for better debugging
5. **Document prerequisites**: List any system requirements
6. **Test on multiple platforms**: Ensure compatibility when possible
7. **Update this README**: Add documentation for your new script

## Script Guidelines

- Use `#!/bin/bash` for bash scripts
- Include comprehensive comments
- Use colored output for better user experience
- Handle Ctrl+C gracefully (trap signals)
- Clean up temporary files and processes
- Return appropriate exit codes
- Support dry-run modes when applicable