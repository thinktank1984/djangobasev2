#!/bin/zsh
# Claude Code launcher script - can be executed directly

# Check if venv exists in current directory and activate it
if [[ -d "venv" ]]; then
    echo "Activating Python virtual environment from $(pwd)..."
    source venv/bin/activate
else
    echo "No virtual environment found in $(pwd), skipping activation..."
fi

# Load nvm if available
if [[ -s "$HOME/.nvm/nvm.sh" ]]; then
    echo "Loading nvm..."
    source "$HOME/.nvm/nvm.sh"
    # If .nvmrc exists in current directory, use it, otherwise use default
    echo "Running nvm use (will use .nvmrc if present)..."
    nvm use default
fi

# Install/update Claude Code
echo "Installing/updating Claude Code..."

# DEBUG: Check nvm and npm status
echo "--- NVM/NPM Debug Info ---"
echo -n "nvm current: "; nvm current
echo -n "which node: "; which node
echo -n "npm prefix: "; npm config get prefix
echo "--------------------------"

# Try without sudo first, fallback to sudo if needed
npm install -g @anthropic-ai/claude-code@1.0.128

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
/Users/ed.sharood2/.npm-global/bin/claude --model claude-sonnet-4-5@20250929  --dangerously-skip-permissions 
