#!/bin/bash

# OpenSpec Installation Script
# This script installs OpenSpec globally via npm and verifies the installation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Node.js version
check_node_version() {
    if command_exists node; then
        NODE_VERSION=$(node --version | sed 's/v//')
        REQUIRED_VERSION="16.0.0"

        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
            log_success "Node.js version $NODE_VERSION meets requirements (>= $REQUIRED_VERSION)"
            return 0
        else
            log_error "Node.js version $NODE_VERSION is too old. Please upgrade to version >= $REQUIRED_VERSION"
            return 1
        fi
    else
        log_error "Node.js is not installed"
        return 1
    fi
}

# Function to check npm version
check_npm_version() {
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        log_success "npm version $NPM_VERSION found"
        return 0
    else
        log_error "npm is not installed"
        return 1
    fi
}

# Function to install Node.js if not present
install_node() {
    log_warning "Node.js is not installed. Attempting to install..."

    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            log "Installing Node.js on Debian/Ubuntu..."
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
        elif command_exists yum; then
            log "Installing Node.js on CentOS/RHEL..."
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
            sudo yum install -y nodejs npm
        elif command_exists dnf; then
            log "Installing Node.js on Fedora..."
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
            sudo dnf install -y nodejs npm
        else
            log_error "Unsupported Linux distribution. Please install Node.js manually from https://nodejs.org/"
            return 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            log "Installing Node.js via Homebrew..."
            brew install node
        else
            log_error "Homebrew not found. Please install Node.js manually from https://nodejs.org/"
            return 1
        fi
    else
        log_error "Unsupported operating system. Please install Node.js manually from https://nodejs.org/"
        return 1
    fi

    # Verify installation
    if check_node_version && check_npm_version; then
        log_success "Node.js and npm installed successfully"
        return 0
    else
        log_error "Node.js installation failed"
        return 1
    fi
}

# Function to install OpenSpec
install_openspec() {
    log "Installing OpenSpec globally..."

    # Check if OpenSpec is already installed
    if command_exists openspec; then
        CURRENT_VERSION=$(openspec --version 2>/dev/null || echo "unknown")
        log_warning "OpenSpec is already installed (version: $CURRENT_VERSION)"

        read -p "Do you want to update OpenSpec to the latest version? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Updating OpenSpec to the latest version..."
            npm uninstall -g @fission-ai/openspec
        else
            log_success "OpenSpec installation skipped"
            return 0
        fi
    fi

    # Install OpenSpec
    if npm install -g @fission-ai/openspec@latest; then
        log_success "OpenSpec installed successfully"
        return 0
    else
        log_error "OpenSpec installation failed"
        return 1
    fi
}

# Function to verify OpenSpec installation
verify_openspec() {
    log "Verifying OpenSpec installation..."

    if command_exists openspec; then
        VERSION=$(openspec --version 2>/dev/null || echo "version unknown")
        log_success "OpenSpec is installed (version: $VERSION)"

        # Test basic functionality
        log "Testing OpenSpec functionality..."
        if openspec --help >/dev/null 2>&1; then
            log_success "OpenSpec is working correctly"
            return 0
        else
            log_warning "OpenSpec is installed but may not be working correctly"
            return 1
        fi
    else
        log_error "OpenSpec installation verification failed"
        return 1
    fi
}

# Function to display usage information
display_usage() {
    echo
    log_success "OpenSpec installation completed successfully!"
    echo
    echo "Usage:"
    echo "  openspec --help          Show help information"
    echo "  openspec --version       Show version information"
    echo "  openspec init            Initialize a new OpenSpec project"
    echo "  openspec generate        Generate specifications from code"
    echo "  openspec validate        Validate specifications"
    echo
    echo "For more information, visit: https://github.com/fission-ai/openspec"
    echo
}

# Main installation function
main() {
    log "Starting OpenSpec installation..."

    # Check if running with appropriate permissions for global npm install
    if [ "$EUID" -ne 0 ]; then
        log_warning "This script installs OpenSpec globally and may require sudo privileges."
        read -p "Do you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Installation cancelled by user"
            exit 0
        fi
    fi

    # Check prerequisites
    log "Checking prerequisites..."

    if ! check_node_version; then
        log "Node.js not found or version too old. Attempting to install..."
        if ! install_node; then
            log_error "Failed to install Node.js. Please install manually and retry."
            exit 1
        fi
    fi

    if ! check_npm_version; then
        log_error "npm not found. Please install Node.js with npm and retry."
        exit 1
    fi

    # Install OpenSpec
    if ! install_openspec; then
        log_error "OpenSpec installation failed"
        exit 1
    fi

    # Verify installation
    if ! verify_openspec; then
        log_error "OpenSpec verification failed"
        exit 1
    fi

    # Display usage information
    display_usage

    log_success "OpenSpec installation completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "OpenSpec Installation Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --version      Show script version"
        echo "  --uninstall    Uninstall OpenSpec"
        echo
        echo "This script installs OpenSpec globally via npm."
        echo "It will check for Node.js and npm prerequisites and install them if needed."
        exit 0
        ;;
    --version)
        echo "OpenSpec Installation Script v1.0.0"
        exit 0
        ;;
    --uninstall)
        log "Uninstalling OpenSpec..."
        if npm uninstall -g @fission-ai/openspec; then
            log_success "OpenSpec uninstalled successfully"
        else
            log_error "OpenSpec uninstallation failed"
            exit 1
        fi
        exit 0
        ;;
    "")
        # No arguments provided, run main installation
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
