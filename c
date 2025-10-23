#!/bin/zsh
# Claude Code launcher script - can be executed directly


# Load nvm if available
if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
    echo "Loading nvm..."
    source "$HOME/.nvm/nvm.sh"
    # If .nvmrc exists in current directory, use it, otherwise use default
    echo "Running nvm use (will use .nvmrc if present)..."
    nvm use default
else
    echo "NVM not found, using system node..."
fi

# Install/update Claude Code
echo "Installing/updating Claude Code..."

# DEBUG: Check nvm and npm status
echo "--- NVM/NPM Debug Info ---"
if command -v nvm &> /dev/null; then
    echo -n "nvm current: "; nvm current 2>/dev/null || echo "N/A"
else
    echo "nvm: not available"
fi
echo -n "which node: "; which node
echo -n "npm prefix: "; npm config get prefix
echo "--------------------------"

# Try with sudo first if we need system-wide installation, then without sudo
if ! npm install -g @anthropic-ai/claude-code@1.0.128 2>/dev/null; then
    echo "Global install failed, trying with sudo..."
    sudo npm install -g @anthropic-ai/claude-code@1.0.128
fi

# Check if Claude Code is available
if ! command -v claude &> /dev/null; then
    echo "❌ Failed to install Claude Code. Please try manually:"
    echo "   npm install -g @anthropic-ai/claude-code"
    echo "   # OR"
    echo "   claude doctor  # for diagnostics"
    exit 1
fi

echo "Starting Claude Code..."

# No arguments - start interactive mode
claude   --dangerously-skip-permissions 
