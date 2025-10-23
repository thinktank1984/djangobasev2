#!/bin/bash
# Type checking script for Django blog application
# Runs Mypy with Django support by default, with local fallback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DOCKER_MODE=true
TARGET_FILES=""

for arg in "$@"; do
    case $arg in
        --local)
            DOCKER_MODE=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] [FILES...]"
            echo ""
            echo "Options:"
            echo "  --local     Run type checking locally (default: local)"
            echo "  --help, -h  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run full type check on Django project"
            echo "  $0 --local                  # Run full type check locally"
            echo "  $0 apps/models.py          # Check specific file"
            echo "  $0 apps/*.py               # Check all files in apps directory"
            exit 0
            ;;
        *)
            TARGET_FILES="$TARGET_FILES $arg"
            ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}    Type Checking with Mypy (Django)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Navigate to runtime directory
cd runtime

# Check if virtual environment exists
if [ -d "../venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source ../venv/bin/activate
fi

# Install mypy and Django stubs if not present
if ! python -c "import mypy" &> /dev/null; then
    echo -e "${YELLOW}Installing mypy and Django stubs...${NC}"
    pip install mypy django-stubs types-requests types-PyYAML
fi

if [ "$DOCKER_MODE" = true ]; then
    echo -e "${YELLOW}Docker mode not yet implemented for Django blog application${NC}"
    echo -e "${YELLOW}Running locally instead...${NC}"
fi

echo -e "${YELLOW}Running locally...${NC}"
echo ""

# Run Mypy with Django support
if [ -z "$TARGET_FILES" ]; then
    echo -e "${BLUE}Checking entire Django project...${NC}"
    mypy --django-settings-module=core.settings --strict-optional --ignore-missing-imports .
else
    echo -e "${BLUE}Checking: $TARGET_FILES${NC}"
    mypy --django-settings-module=core.settings --strict-optional --ignore-missing-imports $TARGET_FILES
fi

EXIT_CODE=$?

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Type checking passed!${NC}"
else
    echo -e "${RED}✗ Type checking failed with errors.${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit $EXIT_CODE

