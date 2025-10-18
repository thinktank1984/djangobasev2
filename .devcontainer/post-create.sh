#!/bin/bash

# Post-creation script for DevPod/VS Code development environment
# This script runs after the container is created to set up the Django development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[SETUP] $1${NC}"
}

log_success() {
    echo -e "${GREEN}[SETUP] ✓ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[SETUP] ⚠ $1${NC}"
}

log_error() {
    echo -e "${RED}[SETUP] ✗ $1${NC}"
}

# Main setup function
main() {
    log "Starting Django development environment setup..."

    # Change to project directory
    cd /workspaces/djangobasev2/blogapp

    # Check if requirements file exists
    if [ -f "requirements.txt" ]; then
        log "Installing Python dependencies..."
        pip install -r requirements.txt
        log_success "Dependencies installed successfully"
    else
        log_warning "requirements.txt not found, skipping Python dependencies installation"
    fi

    # Run Django system checks
    log "Running Django system checks..."
    if python manage.py check --deploy; then
        log_success "Django system checks passed"
    else
        log_warning "Django system checks completed with warnings"
    fi

    # Run database migrations (only if database is accessible)
    log "Applying database migrations..."
    if python manage.py migrate --noinput; then
        log_success "Database migrations applied successfully"
    else
        log_warning "Database migrations completed with warnings"
    fi

    # Collect static files
    log "Collecting static files..."
    if python manage.py collectstatic --noinput; then
        log_success "Static files collected successfully"
    else
        log_warning "Static files collection completed with warnings"
    fi

    # Check if Tailwind CSS is configured
    if [ -f "tailwind.config.js" ] || [ -f "theme/static_src/tailwind.config.js" ]; then
        log "Tailwind CSS configuration detected, installing Node.js dependencies..."
        if [ -f "package.json" ]; then
            npm install
            log_success "Node.js dependencies installed"
        else
            log_warning "package.json not found, skipping Node.js dependencies installation"
        fi
    fi

    # Create superuser script for convenience
    log "Creating convenience scripts..."

    # Create a script to create superuser
    cat > createsuperuser.sh << 'EOF'
#!/bin/bash
echo "Creating Django superuser..."
cd /workspaces/djangobasev2/blogapp
python manage.py createsuperuser
EOF
    chmod +x createsuperuser.sh

    # Create a script to run tests
    cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "Running Django tests..."
cd /workspaces/djangobasev2/blogapp
python manage.py test
EOF
    chmod +x run_tests.sh

    # Create a script to start development server
    cat > start_server.sh << 'EOF'
#!/bin/bash
echo "Starting Django development server on http://localhost:8000..."
cd /workspaces/djangobasev2/blogapp
python manage.py runserver 0.0.0.0:8000
EOF
    chmod +x start_server.sh

    log_success "Convenience scripts created"

    # Display setup completion message
    echo
    log_success "🎉 Django development environment setup completed!"
    echo
    echo "🚀 Quick Start Commands:"
    echo "  ./start_server.sh    - Start Django development server"
    echo "  ./createsuperuser.sh - Create admin superuser"
    echo "  ./run_tests.sh       - Run Django tests"
    echo
    echo "📝 Django Management Commands:"
    echo "  python manage.py runserver 0.0.0.0:8000  - Start development server"
    echo "  python manage.py migrate                 - Run migrations"
    echo "  python manage.py createsuperuser          - Create admin user"
    echo "  python manage.py shell                   - Open Django shell"
    echo "  python manage.py collectstatic           - Collect static files"
    echo "  python manage.py test                     - Run tests"
    echo
    echo "🌐 Access your application at: http://localhost:8000"
    echo "🔧 Admin interface at: http://localhost:8000/admin"
    echo
    echo "📚 Useful Tips:"
    echo "  - Use the VS Code terminal to run Django commands"
    echo "  - The debugger is configured for Django applications"
    echo "  - Static files are automatically collected"
    echo "  - Database migrations are applied automatically"
    echo
    log "Setup complete. Happy coding! 🐍"
}

# Run the main setup
main "$@"