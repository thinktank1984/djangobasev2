#!/bin/bash

# Bloggy Setup Script
# This script sets up the Emmett-based Bloggy example application.
# Supports both Docker and local development modes.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
USE_DOCKER=true
FORCE_REBUILD=false

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
        --rebuild|-r)
            FORCE_REBUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --docker, -d     Setup for Docker (default)"
            echo "  --local, -l      Setup for local development"
            echo "  --rebuild, -r    Force Docker rebuild"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
    esac
done

if [ "$USE_DOCKER" = true ]; then
    echo -e "${BLUE}🚀 Setting up Runtime Application (Docker mode)...${NC}"
else
    echo -e "${BLUE}🚀 Setting up Runtime Application (local mode)...${NC}"
fi
echo ""

# Navigate to project root
cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)
SETUP_DIR="$PROJECT_ROOT/setup"
CONFIG_FILE="$SETUP_DIR/setup_config.json"

echo -e "${GREEN}✅ Project root: $PROJECT_ROOT${NC}"

# Function to check if Docker rebuild is needed
should_rebuild_docker() {
    if [ "$FORCE_REBUILD" = true ]; then
        return 0  # Force rebuild
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        return 0  # No config file, need rebuild
    fi
    
    # Read config file
    REBUILD_FLAG=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('rebuild_docker', True))" 2>/dev/null || echo "true")
    
    if [ "$REBUILD_FLAG" = "True" ] || [ "$REBUILD_FLAG" = "true" ]; then
        return 0  # Config says rebuild
    fi
    
    return 1  # No rebuild needed
}

# Function to update config file
update_config() {
    local rebuild_value=$1
    mkdir -p "$SETUP_DIR"
    echo "{\"rebuild_docker\":$rebuild_value}" > "$CONFIG_FILE"
}

if [ "$USE_DOCKER" = true ]; then
    # ============================================================================
    # DOCKER MODE SETUP
    # ============================================================================
    
    echo -e "${BLUE}Checking Docker requirements...${NC}"
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is required but not installed.${NC}"
        echo "Install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if docker compose is available
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is required but not available.${NC}"
        echo "Update Docker to get Compose V2"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker detected${NC}"
    
    # Check if rebuild is needed
    if should_rebuild_docker; then
        echo ""
        echo -e "${YELLOW}🔨 Docker build required...${NC}"
        cd docker
        docker compose build runtime
        cd ..
        update_config false
        echo -e "${GREEN}✅ Docker image built${NC}"
    else
        echo -e "${GREEN}✅ Docker image up to date (use --rebuild to force)${NC}"
    fi
    
    # Setup database if needed (run migrations)
    echo ""
    echo -e "${BLUE}Checking database setup...${NC}"
    
    # Check if database exists
    if [ ! -f "$PROJECT_ROOT/runtime/databases/bloggy.db" ]; then
        echo -e "${YELLOW}⚠️  Database not found. Setting up...${NC}"
        
        # Start container temporarily to run migrations
        cd docker
        docker compose up -d runtime
        sleep 3
        
        docker compose exec runtime emmett migrations up 2>/dev/null || true
        docker compose exec runtime emmett setup 2>/dev/null || true
        
        docker compose down
        cd ..
        
        echo -e "${GREEN}✅ Database setup complete${NC}"
    else
        echo -e "${GREEN}✅ Database exists${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 Docker Setup Complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BLUE}📋 Next steps:${NC}"
    echo ""
    echo "1️⃣  Start the application:"
    echo -e "   ${YELLOW}./run_bloggy.sh${NC}"
    echo "   Or:"
    echo -e "   ${YELLOW}just runtime${NC}        # Foreground"
    echo -e "   ${YELLOW}just runtime-bg${NC}     # Background"
    echo ""
    echo "2️⃣  Access the application:"
    echo "   • Application: http://localhost:8081/"
    echo "   • Login with:"
    echo "     - Email: doc@emmettbrown.com"
    echo "     - Password: fluxcapacitor"
    echo ""
    
    exit 0
fi

# ============================================================================
# LOCAL MODE SETUP
# ============================================================================

# Check Python version
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    echo "Please install Python 3.9+ and try again."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    echo -e "${RED}❌ Python 3.9+ is required (you have $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"

# Check and install uv
echo ""
echo -e "${BLUE}Checking uv package manager...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}⚠️  uv not found. Installing uv (fast Python package installer)...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv installation failed or not in PATH${NC}"
        echo "Please run one of:"
        echo "  source ~/.bashrc    # for bash"
        echo "  source ~/.zshrc     # for zsh"
        echo "Then run this script again."
        exit 1
    fi
fi

UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
echo -e "${GREEN}✅ uv is available: $UV_VERSION${NC}"

# Create virtual environment in project root
echo ""
echo -e "${BLUE}Setting up virtual environment...${NC}"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment in project root..."
    uv venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Install Emmett and dependencies
echo ""
echo -e "${BLUE}Installing Emmett framework and dependencies...${NC}"
uv pip install --python venv/bin/python emmett>=2.5.0
uv pip install --python venv/bin/python pytest>=7.0.0

echo -e "${GREEN}✅ Dependencies installed${NC}"

# Run database migrations
echo ""
echo -e "${BLUE}Setting up database...${NC}"
cd runtime || exit 1

# Create databases directory if it doesn't exist
mkdir -p databases

# Check if migrations exist and run them
if [ -d "migrations" ] && [ "$(ls -A migrations/*.py 2>/dev/null)" ]; then
    echo "Applying migrations..."
    if uv run --python ../venv/bin/python emmett migrations up; then
        echo -e "${GREEN}✅ Migrations applied${NC}"
    else
        echo -e "${YELLOW}⚠️  Migration failed - trying to generate initial migration...${NC}"
        uv run --python ../venv/bin/python emmett migrations generate
        uv run --python ../venv/bin/python emmett migrations up || {
            echo -e "${RED}❌ Migrations failed${NC}"
        }
    fi
else
    echo "No migrations found, generating initial migration..."
    uv run --python ../venv/bin/python emmett migrations generate
    uv run --python ../venv/bin/python emmett migrations up || {
        echo -e "${RED}❌ Migrations failed${NC}"
    }
fi

# Setup admin user
echo ""
echo -e "${BLUE}Setting up admin user...${NC}"
if uv run --python ../venv/bin/python emmett setup; then
    echo -e "${GREEN}✅ Admin user created${NC}"
else
    echo -e "${RED}❌ Admin setup failed${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Local Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1️⃣  Start the application:"
echo -e "   ${YELLOW}./run_bloggy.sh --local${NC}"
echo "   Or:"
echo -e "   ${YELLOW}just runtime-local${NC}"
echo "   Or manually:"
echo -e "   ${YELLOW}cd runtime && uv run emmett develop${NC}"
echo ""
echo "2️⃣  Access the application:"
echo "   • Application: http://localhost:8000/"
echo "   • Login with:"
echo "     - Email: doc@emmettbrown.com"
echo "     - Password: fluxcapacitor"
echo ""
echo "3️⃣  Run tests (coverage enabled by default):"
echo -e "   ${YELLOW}./run_tests.sh${NC}"
echo "   Or manually:"
echo -e "   ${YELLOW}cd runtime && uv run pytest tests.py${NC}"
echo ""
echo -e "${BLUE}📚 About the Runtime Application:${NC}"
echo "   This is a micro-blogging application built with Emmett framework."
echo "   It demonstrates:"
echo "   • User authentication and authorization"
echo "   • Database models and ORM"
echo "   • Form handling and validation"
echo "   • Template rendering"
echo "   • Admin-only features"
echo ""
echo -e "${BLUE}📖 Emmett Documentation:${NC}"
echo "   See emmett_documentation/ for comprehensive framework docs"
echo ""
echo -e "${GREEN}Happy coding! 📝${NC}"
echo ""

