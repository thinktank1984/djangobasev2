#!/bin/bash

# Django Blog Application Run Script
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
        echo -e "${BLUE}🚀 Starting Django Blog Application in Docker (background)...${NC}"
    else
        echo -e "${BLUE}🚀 Starting Django Blog Application in Docker (foreground)...${NC}"
    fi
else
    echo -e "${BLUE}🚀 Starting Django Blog Application (local mode)...${NC}"
fi
echo ""

# Run environment setup checks
echo -e "${BLUE}Running setup checks...${NC}"
if [ "$USE_DOCKER" = true ]; then
    echo -e "${YELLOW}⚠️ Docker mode not yet implemented for Django blog application${NC}"
    echo -e "${YELLOW}   Using local mode instead${NC}"
    USE_DOCKER=false
fi

# Run Django migrations and checks
echo -e "${BLUE}Running Django migrations...${NC}"
cd blogapp
if python manage.py migrate --check; then
    echo -e "${GREEN}✅ Database is up to date${NC}"
else
    echo -e "${BLUE}Applying pending migrations...${NC}"
    python manage.py migrate
    echo -e "${GREEN}✅ Migrations applied successfully${NC}"
fi

echo -e "${BLUE}Running Django system checks...${NC}"
if python manage.py check; then
    echo -e "${GREEN}✅ Django system checks passed${NC}"
else
    echo -e "${YELLOW}⚠ Django system checks found issues (see output above)${NC}"
fi
cd "$PROJECT_ROOT"
echo ""

if [ "$USE_DOCKER" = true ]; then
    # ============================================================================
    # DOCKER MODE
    # ============================================================================
    
    echo "Access the Django Blog Application at:"
    echo "  Blog App: ${GREEN}http://localhost:8000${NC}"
    echo "  Admin:    ${GREEN}http://localhost:8000/admin${NC}"
    echo ""
    echo "Create a superuser to access the admin panel:"
    echo "  ${BLUE}cd blogapp && python manage.py createsuperuser${NC}"
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
    
    # Install dependencies and check environment
    echo -e "${BLUE}Checking Python environment...${NC}"
    cd blogapp

    # Check if virtual environment exists, create if needed
    if [ ! -d "../venv" ]; then
        echo -e "${BLUE}Creating virtual environment...${NC}"
        cd "$PROJECT_ROOT"
        python -m venv venv
        cd blogapp
    fi

    # Activate virtual environment
    source ../venv/bin/activate

    # Install dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install -r requirements.txt > /dev/null 2>&1

    # Check if .env file exists, create from example if needed
    if [ ! -f ".env" ]; then
        echo -e "${BLUE}Creating .env file from example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}⚠ Please update .env file with your configuration${NC}"
    fi

    # Collect static files
    echo -e "${BLUE}Collecting static files...${NC}"
    python manage.py collectstatic --noinput

    echo -e "${GREEN}✅ Setup complete! Starting Django development server...${NC}"
    echo ""
    echo "Access the Django Blog Application at:"
    echo "  Blog App: ${GREEN}http://localhost:8000${NC}"
    echo "  Admin:    ${GREEN}http://localhost:8000/admin${NC}"
    echo ""
    echo "Create a superuser to access the admin panel:"
    echo "  ${BLUE}python manage.py createsuperuser${NC}"
    echo ""
    echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
    echo ""

    # Start the Django development server
    python manage.py runserver
fi

