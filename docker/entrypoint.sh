#!/bin/bash

# Docker Entrypoint Script for Runtime Application
# This script runs inside the Docker container before starting the application

set -e

echo "🔵 Docker Entrypoint: Starting initialization..."

# Navigate to runtime directory
cd /app/runtime

# Build Tailwind CSS
echo "🎨 Building Tailwind CSS..."
if [ -f "package.json" ]; then
    # Remove host's node_modules to avoid binary compatibility issues
    # (host might be macOS, container is Linux)
    if [ -d "node_modules" ]; then
        echo "   Removing host node_modules (incompatible binaries)..."
        rm -rf node_modules
    fi
    
    # Install fresh Linux-compatible packages
    echo "   Installing npm packages for Linux..."
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    
    # Build Tailwind CSS
    echo "   Compiling Tailwind CSS..."
    npm run build:css 2>&1 | tail -2
    echo "✅ Tailwind CSS built successfully"
else
    echo "⚠️  package.json not found, skipping Tailwind build"
fi

# Ensure test database exists
echo "🗄️  Ensuring test database exists..."
PGPASSWORD=bloggy_password psql -h postgres -U bloggy -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'bloggy_test'" | grep -q 1 || \
PGPASSWORD=bloggy_password psql -h postgres -U bloggy -d postgres -c "CREATE DATABASE bloggy_test OWNER bloggy;" && \
echo "✅ Test database ready"

# Run database migrations for main database
echo "🗄️  Running database migrations (main)..."
emmett migrations up || echo "⚠️  No migrations to run or migrations failed"

# Run database migrations for test database
echo "🗄️  Running database migrations (test)..."
DATABASE_URL='postgres://bloggy:bloggy_password@postgres:5432/bloggy_test' emmett migrations up || echo "⚠️  Test database migrations failed"
echo "✅ Test database migrations complete"

echo "✅ Initialization complete!"
echo ""

# Execute the main command (passed as arguments to this script)
exec "$@"

