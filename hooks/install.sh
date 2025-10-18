#!/bin/bash
# Install git hooks for the project

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Get project root
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
fi

cd "$PROJECT_ROOT" || exit 1

echo -e "${BLUE}Installing git hooks...${NC}"
echo ""

# Check if hooks directory exists
if [ ! -d "hooks" ]; then
    echo -e "${RED}❌ Error: hooks directory not found${NC}"
    exit 1
fi

# Install pre-commit hook
if [ -f "hooks/pre-commit" ]; then
    cp hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✅ Installed pre-commit hook${NC}"
    echo "   - Validates Emmett models before commit"
    echo "   - Blocks commits with model anti-patterns (errors)"
    echo "   - Allows warnings (can be reviewed later)"
else
    echo -e "${RED}❌ Error: hooks/pre-commit not found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Git hooks installed successfully${NC}"
echo ""
echo "The pre-commit hook will run automatically on 'git commit'"
echo "To bypass the hook (not recommended): git commit --no-verify"
echo ""
echo "To uninstall hooks: rm .git/hooks/pre-commit"

