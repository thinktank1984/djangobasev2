#!/bin/bash
# Type checking script for pybase project
# Runs Pyright in Docker container by default, with local fallback

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
            echo "  --local     Run type checking locally (default: Docker)"
            echo "  --help, -h  Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run full type check in Docker"
            echo "  $0 --local                  # Run full type check locally"
            echo "  $0 runtime/app.py          # Check specific file in Docker"
            echo "  $0 --local runtime/*.py    # Check specific files locally"
            exit 0
            ;;
        *)
            TARGET_FILES="$TARGET_FILES $arg"
            ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}    Type Checking with Pyright${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ "$DOCKER_MODE" = true ]; then
    echo -e "${YELLOW}Running in Docker container...${NC}"
    echo ""
    
    # Check if Docker container is running
    if ! docker compose -f docker/docker-compose.yaml ps runtime | grep -q "Up"; then
        echo -e "${YELLOW}Starting Docker container...${NC}"
        docker compose -f docker/docker-compose.yaml up -d runtime
        echo -e "${GREEN}Container started.${NC}"
        echo ""
    fi
    
    # Run Pyright in Docker
    if [ -z "$TARGET_FILES" ]; then
        echo -e "${BLUE}Checking entire project...${NC}"
        docker compose -f docker/docker-compose.yaml exec runtime pyright --project /app/setup/pyrightconfig.json
    else
        echo -e "${BLUE}Checking: $TARGET_FILES${NC}"
        docker compose -f docker/docker-compose.yaml exec runtime pyright --project /app/setup/pyrightconfig.json $TARGET_FILES
    fi
    
    EXIT_CODE=$?
else
    echo -e "${YELLOW}Running locally...${NC}"
    echo ""
    
    # Check if pyright is installed locally
    if ! command -v pyright &> /dev/null; then
        echo -e "${RED}ERROR: Pyright not found locally.${NC}"
        echo -e "${YELLOW}Install with: uv pip install pyright${NC}"
        echo -e "${YELLOW}Or run without --local to use Docker.${NC}"
        exit 1
    fi
    
    # Run Pyright locally
    if [ -z "$TARGET_FILES" ]; then
        echo -e "${BLUE}Checking entire project...${NC}"
        pyright --project setup/pyrightconfig.json
    else
        echo -e "${BLUE}Checking: $TARGET_FILES${NC}"
        pyright --project setup/pyrightconfig.json $TARGET_FILES
    fi
    
    EXIT_CODE=$?
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Type checking passed!${NC}"
else
    echo -e "${RED}✗ Type checking failed with errors.${NC}"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

exit $EXIT_CODE

