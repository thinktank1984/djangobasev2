#!/bin/bash

# DevPod Configuration Validation Script
# This script validates the DevPod setup before deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[VALIDATION] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[VALIDATION] ✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[VALIDATION] ⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}[VALIDATION] ✗ $1${NC}"
}

# Validation counters
VALIDATIONS_PASSED=0
VALIDATIONS_FAILED=0

# Function to record validation result
validation_passed() {
    log_success "$1"
    ((VALIDATIONS_PASSED++))
}

validation_failed() {
    log_error "$1"
    ((VALIDATIONS_FAILED++))
}

validation_warning() {
    log_warning "$1"
}

# Main validation function
main() {
    log "Starting DevPod configuration validation..."

    # Check if required files exist
    log "Checking required configuration files..."

    if [ -f "devpod.yaml" ]; then
        validation_passed "devpod.yaml exists"
    else
        validation_failed "devpod.yaml is missing"
    fi

    if [ -f "devcontainer.json" ]; then
        validation_passed "devcontainer.json exists"
    else
        validation_failed "devcontainer.json is missing"
    fi

    if [ -f "Dockerfile" ]; then
        validation_passed "Dockerfile exists"
    else
        validation_failed "Dockerfile is missing"
    fi

    if [ -f "docker-compose.yml" ]; then
        validation_passed "docker-compose.yml exists"
    else
        validation_failed "docker-compose.yml is missing"
    fi

    if [ -f "post-create.sh" ]; then
        validation_passed "post-create.sh exists"
        if [ -x "post-create.sh" ]; then
            validation_passed "post-create.sh is executable"
        else
            validation_failed "post-create.sh is not executable"
        fi
    else
        validation_failed "post-create.sh is missing"
    fi

    # Check environment files
    log "Checking environment configuration files..."

    if [ -f ".env.example" ]; then
        validation_passed ".env.example exists"
    else
        validation_failed ".env.example is missing"
    fi

    if [ -f ".env.development" ]; then
        validation_passed ".env.development exists"
    else
        validation_failed ".env.development is missing"
    fi

    if [ -f ".env.devpod" ]; then
        validation_passed ".env.devpod exists"
    else
        validation_failed ".env.devpod is missing"
    fi

    # Validate DevPod YAML structure (basic checks)
    if [ -f "devpod.yaml" ]; then
        log "Validating devpod.yaml structure..."

        if grep -q "^version:" devpod.yaml; then
            validation_passed "devpod.yaml has version field"
        else
            validation_failed "devpod.yaml missing version field"
        fi

        if grep -q "^name:" devpod.yaml; then
            validation_passed "devpod.yaml has name field"
        else
            validation_failed "devpod.yaml missing name field"
        fi

        if grep -q "^ide:" devpod.yaml; then
            validation_passed "devpod.yaml has ide configuration"
        else
            validation_failed "devpod.yaml missing ide configuration"
        fi

        if grep -q "^dev:" devpod.yaml; then
            validation_passed "devpod.yaml has dev configuration"
        else
            validation_failed "devpod.yaml missing dev configuration"
        fi
    fi

    # Validate Dockerfile
    if [ -f "Dockerfile" ]; then
        log "Validating Dockerfile..."

        if grep -q "^FROM" Dockerfile; then
            validation_passed "Dockerfile has FROM instruction"
        else
            validation_failed "Dockerfile missing FROM instruction"
        fi

        if grep -q "python" Dockerfile; then
            validation_passed "Dockerfile includes Python"
        else
            validation_warning "Dockerfile might not include Python"
        fi

        if grep -q "WORKDIR" Dockerfile; then
            validation_passed "Dockerfile has WORKDIR instruction"
        else
            validation_warning "Dockerfile missing WORKDIR instruction"
        fi
    fi

    # Validate docker-compose.yml
    if [ -f "docker-compose.yml" ]; then
        log "Validating docker-compose.yml..."

        if grep -q "^version:" docker-compose.yml; then
            validation_passed "docker-compose.yml has version field"
        else
            validation_warning "docker-compose.yml missing version field (optional for newer versions)"
        fi

        if grep -q "^services:" docker-compose.yml; then
            validation_passed "docker-compose.yml has services section"
        else
            validation_failed "docker-compose.yml missing services section"
        fi

        if grep -q "db:" docker-compose.yml; then
            validation_passed "docker-compose.yml has database service"
        else
            validation_warning "docker-compose.yml missing database service"
        fi
    fi

    # Check for common issues
    log "Checking for common configuration issues..."

    # Check if port 8000 is configured (Django default)
    if grep -q "8000" devpod.yaml || grep -q "8000" devcontainer.json; then
        validation_passed "Django port 8000 is configured"
    else
        validation_warning "Django port 8000 not explicitly configured"
    fi

    # Check if VS Code extensions are configured
    if grep -q "extensions" devcontainer.json; then
        validation_passed "VS Code extensions are configured"
    else
        validation_warning "No VS Code extensions configured"
    fi

    # Check if Python packages are installed
    if grep -q "pip install\|python -m pip" Dockerfile || grep -q "requirements.txt" Dockerfile; then
        validation_passed "Python package installation is configured"
    else
        validation_warning "Python package installation not explicitly configured"
    fi

    # Validate paths and references
    log "Validating path references..."

    if [ -f "../blogapp/requirements.txt" ]; then
        validation_passed "blogapp/requirements.txt exists"
    else
        validation_warning "blogapp/requirements.txt not found - Django dependencies may not be installed"
    fi

    if [ -d "../blogapp" ]; then
        validation_passed "Django project directory (blogapp) exists"
    else
        validation_failed "Django project directory (blogapp) not found"
    fi

    # Summary
    echo
    log "Validation Summary:"
    log "✅ Passed: $VALIDATIONS_PASSED"
    log "❌ Failed: $VALIDATIONS_FAILED"

    if [ $VALIDATIONS_FAILED -eq 0 ]; then
        echo
        log_success "🎉 All validations passed! DevPod configuration is ready to use."
        echo
        echo "Next steps:"
        echo "  1. Install DevPod CLI: curl -fsSL https://raw.githubusercontent.com/loft-sh/devpod/main/install.sh | bash"
        echo "  2. Start development environment: devpod up"
        echo "  3. Or open in VS Code: devpod up --ide vscode"
        echo
        exit 0
    else
        echo
        log_error "❌ $VALIDATIONS_FAILED validation(s) failed. Please fix the issues above before using DevPod."
        echo
        exit 1
    fi
}

# Run validation
main "$@"