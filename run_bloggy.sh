#!/bin/bash

# Runtime Application Run Script
# Supports both Docker and local development modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Navigate to project root
cd "$(dirname "$0")" || exit 1
PROJECT_ROOT=$(pwd)

# Parse command line arguments
USE_DOCKER=true      # Default to Docker
USE_BACKGROUND=true  # Default to background

for arg in "$@"; do
    case $arg in
        --local|-l)
            USE_DOCKER=false
            shift
            ;;
        --docker|-d)
            USE_DOCKER=true
            shift
            ;;
        --background|-b)
            USE_BACKGROUND=true
            shift
            ;;
        --foreground|-f)
            USE_BACKGROUND=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker, -d       Run in Docker (default)"
            echo "  --local, -l        Run locally with uv"
            echo "  --background, -b   Run in background (default for Docker)"
            echo "  --foreground, -f   Run in foreground"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run in Docker (background)"
            echo "  $0 --foreground    # Run in Docker (foreground)"
            echo "  $0 --local         # Run locally"
            exit 0
            ;;
    esac
done

if [ "$USE_DOCKER" = true ]; then
    if [ "$USE_BACKGROUND" = true ]; then
        echo -e "${BLUE}🚀 Starting Runtime Application in Docker (background)...${NC}"
    else
        echo -e "${BLUE}🚀 Starting Runtime Application in Docker (foreground)...${NC}"
    fi
else
    echo -e "${BLUE}🚀 Starting Runtime Application (local mode)...${NC}"
fi
echo ""

# Run setup script first to ensure environment is ready
echo -e "${BLUE}Running setup checks...${NC}"
if [ "$USE_DOCKER" = true ]; then
    "$PROJECT_ROOT/setup/setup.sh" --docker
else
    "$PROJECT_ROOT/setup/setup.sh" --local
fi
echo ""

# Validate models for anti-patterns
echo -e "${BLUE}Validating Emmett models...${NC}"
if [ "$USE_DOCKER" = true ]; then
    docker compose -f docker/docker-compose.yaml exec -T runtime python validate_models.py --all --severity warning 2>/dev/null || {
        echo -e "${YELLOW}⚠ Model validation skipped (container not running or validation failed)${NC}"
    }
else
    cd runtime
    if python validate_models.py --all --severity warning; then
        echo -e "${GREEN}✅ Model validation passed${NC}"
    else
        echo -e "${YELLOW}⚠ Model validation found issues (see output above)${NC}"
    fi
    cd "$PROJECT_ROOT"
fi
echo ""

if [ "$USE_DOCKER" = true ]; then
    # ============================================================================
    # DOCKER MODE
    # ============================================================================
    
    echo "Access the services at:"
    echo "  Runtime App: ${GREEN}http://localhost:8081${NC}"
    echo "  Bugsink:     ${GREEN}http://localhost:8000${NC}"
    echo "  Prometheus:  ${GREEN}http://localhost:9090${NC}"
    echo "  Grafana:     ${GREEN}http://localhost:3000${NC}"
    echo "  cAdvisor:    ${GREEN}http://localhost:8080${NC}"
    echo ""
    echo "Login to Runtime App with:"
    echo "  Email: ${YELLOW}doc@emmettbrown.com${NC}"
    echo "  Password: ${YELLOW}fluxcapacitor${NC}"
    echo ""
    
    # Run docker compose (without --build since setup.sh handles that)
    cd docker
    if [ "$USE_BACKGROUND" = true ]; then
        docker compose up -d
        echo -e "${GREEN}✅ All services started in background${NC}"
        echo ""
        echo "To view logs: ${BLUE}docker compose -f docker/docker-compose.yaml logs -f${NC}"
        echo "Or use: ${BLUE}just runtime-logs${NC}"
        echo ""
        echo "To stop: ${BLUE}docker compose -f docker/docker-compose.yaml down${NC}"
        echo "Or use: ${BLUE}just down${NC}"
    else
        echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
        echo ""
        docker compose up
    fi
    
else
    # ============================================================================
    # LOCAL MODE
    # ============================================================================
    
    # Build Tailwind CSS before starting server
    echo -e "${BLUE}Building Tailwind CSS...${NC}"
    cd runtime
    if command -v npm &> /dev/null; then
        npm install --silent 2>&1 | grep -v "npm WARN" || true
        npm run build:css
        echo -e "${GREEN}✅ Tailwind CSS built successfully${NC}"
    else
        echo -e "${RED}❌ npm not found! Please install Node.js and npm${NC}"
        echo "   Visit: https://nodejs.org/"
        exit 1
    fi
    echo ""
    
    echo -e "${GREEN}✅ Setup complete! Starting development server...${NC}"
    echo ""
    echo "Access the application at: ${GREEN}http://localhost:8000${NC}"
    echo ""
    echo "Login with:"
    echo "  Email: ${YELLOW}doc@emmettbrown.com${NC}"
    echo "  Password: ${YELLOW}fluxcapacitor${NC}"
    echo ""
    echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
    echo ""
    
    # Start the server
    uv run --python ../venv/bin/python emmett develop
fi

