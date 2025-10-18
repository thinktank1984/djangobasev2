#!/bin/bash

# DevPod Quick Start Script for DjangoBaseV2
# This script helps you get started with DevPod quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[QUICKSTART] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[QUICKSTART] ✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[QUICKSTART] ⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}[QUICKSTART] ✗ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main function
main() {
    log "🚀 DjangoBaseV2 DevPod Quick Start"
    echo

    # Check if DevPod is installed
    if command_exists devpod; then
        log_success "DevPod CLI is installed"
        devpod version
    else
        log_error "DevPod CLI is not installed"
        echo
        log "Installing DevPod CLI..."
        curl -fsSL https://raw.githubusercontent.com/loft-sh/devpod/main/install.sh | bash
        echo
        log_success "DevPod CLI installed successfully"
    fi

    # Check if Docker is running
    if command_exists docker && docker info >/dev/null 2>&1; then
        log_success "Docker is running"
    else
        log_error "Docker is not running or not installed"
        log "Please start Docker and try again"
        exit 1
    fi

    # Validate DevPod configuration
    if [ -f ".devcontainer/validate.sh" ]; then
        log "Validating DevPod configuration..."
        if .devcontainer/validate.sh; then
            log_success "DevPod configuration is valid"
        else
            log_warning "DevPod configuration validation completed with warnings"
        fi
    else
        log_warning "Validation script not found"
    fi

    echo
    log "🎯 Quick Start Options:"
    echo
    echo "1. Start DevPod environment (VS Code):"
    echo "   devpod up --ide vscode"
    echo
    echo "2. Start DevPod environment (CLI):"
    echo "   devpod up"
    echo "   devpod ssh"
    echo
    echo "3. Start DevPod with custom IDE:"
    echo "   devpod up --ide pycharm"
    echo "   devpod up --ide intellij"
    echo
    echo "4. Stop DevPod environment:"
    echo "   devpod stop"
    echo
    echo "5. Delete DevPod environment:"
    echo "   devpod delete"
    echo

    log "📚 Useful commands once inside DevPod:"
    echo "  cd blogapp"
    echo "  python manage.py runserver 0.0.0.0:8000"
    echo "  python manage.py migrate"
    echo "  python manage.py createsuperuser"
    echo

    log "🌐 Access your application at: http://localhost:8000"
    log "🔧 Admin interface at: http://localhost:8000/admin"
    echo

    log_success "Ready to start Django development with DevPod! 🐍"
}

# Help function
show_help() {
    echo "DjangoBaseV2 DevPod Quick Start Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --validate     Only run validation"
    echo "  --start        Start DevPod environment"
    echo "  --stop         Stop DevPod environment"
    echo "  --status       Show DevPod status"
    echo
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --validate)
        if [ -f ".devcontainer/validate.sh" ]; then
            .devcontainer/validate.sh
        else
            log_error "Validation script not found"
            exit 1
        fi
        exit 0
        ;;
    --start)
        log "Starting DevPod environment..."
        if devpod up --ide vscode; then
            log_success "DevPod environment started successfully"
        else
            log_error "Failed to start DevPod environment"
            exit 1
        fi
        exit 0
        ;;
    --stop)
        log "Stopping DevPod environment..."
        if devpod stop; then
            log_success "DevPod environment stopped successfully"
        else
            log_error "Failed to stop DevPod environment"
            exit 1
        fi
        exit 0
        ;;
    --status)
        log "DevPod environment status:"
        echo
        devpod list
        exit 0
        ;;
    "")
        # No arguments, run main quick start
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac