#!/bin/sh

# Gemini Code launcher with automatic dependency installation
# This script checks for and installs nvm, Node.js, and Gemini CLI if missing

set -e  # Exit on error

echo "🚀 Gemini Code Launcher"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if nvm is installed
export NVM_DIR="$HOME/.nvm"

if [ ! -d "$NVM_DIR" ] || [ ! -s "$NVM_DIR/nvm.sh" ]; then
    echo "📦 Installing nvm (Node Version Manager)..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    
    # Reload the script to load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    
    if [ ! -s "$NVM_DIR/nvm.sh" ]; then
        echo "❌ Failed to install nvm"
        exit 1
    fi
    echo "✅ nvm installed successfully"
else
    # Load nvm
    . "$NVM_DIR/nvm.sh"
    echo "✅ nvm found"
fi

# Check if Node.js is installed
if ! command -v node > /dev/null 2>&1; then
    echo "📦 Installing Node.js v24.9.0..."
    nvm install 24.9.0
    nvm use 24.9.0
    echo "✅ Node.js installed"
else
    # Use Node 24.9.0 if not already using it
    nvm install 24.9.0 2>/dev/null || true
    nvm use 24.9.0
    NODE_VERSION=$(node -v)
    echo "✅ Node.js $NODE_VERSION ready"
fi

# Get Node.js version and paths
NODE_VERSION_WITH_V=$(node -v)
NODE_VERSION=$(echo "$NODE_VERSION_WITH_V" | sed 's/^v//')
NVM_NPM_PATH="$NVM_DIR/versions/node/v$NODE_VERSION/bin/npm"
NVM_NODE_PREFIX="$NVM_DIR/versions/node/v$NODE_VERSION"
export NPM_CONFIG_PREFIX="$NVM_NODE_PREFIX"
export PATH="$NVM_NODE_PREFIX/bin:$PATH"

# Check if Gemini CLI is installed
if ! command -v gemini > /dev/null 2>&1; then
    echo "📦 Installing Gemini CLI..."
    "$NVM_NPM_PATH" install -g @google/gemini-cli@latest
    echo "✅ Gemini CLI installed"
else
    echo "✅ Gemini CLI found"
    # Optional: Update to latest version
    echo "🔄 Checking for Gemini CLI updates..."
    "$NVM_NPM_PATH" install -g @google/gemini-cli@latest 2>/dev/null || true
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Environment Info:"
echo "  Node: $(node -v)"
echo "  npm:  $(npm -v)"
echo "  Gemini CLI: $(gemini --version 2>/dev/null || echo 'installed')"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if venv exists and activate it
if [ -d "venv" ]; then
    echo "🐍 Activating Python virtual environment..."
    . ./venv/bin/activate
else
    echo "ℹ️  No Python venv found in $(pwd)"
fi

echo ""
echo "🎯 Starting Gemini Code..."
echo ""

# Set API key and launch
GEMINI_API_KEY="AIzaSyBLSp-lpMjgZKhFZM7KEi9q63dOUyQ_qlY" gemini --sandbox=disabled --yolo