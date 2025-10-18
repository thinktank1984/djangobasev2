#!/bin/bash
# Host setup script (Django)
# Created from setup.sh: removed Docker and replaced Emmett with Django
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

FORCE_REBUILD=false

for arg in "$@"; do
    case $arg in
        --rebuild|-r)
            FORCE_REBUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --rebuild, -r    Recreate virtualenv and reinstall dependencies"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}🚀 Setting up Runtime Application (host/Django mode)...${NC}"
echo ""

cd "$(dirname "$0")/.." || exit 1
PROJECT_ROOT=$(pwd)
SETUP_DIR="$PROJECT_ROOT/setup"

echo -e "${GREEN}✅ Project root: $PROJECT_ROOT${NC}"

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" 2>/dev/null; then
    PYVER=$(python3 --version 2>/dev/null)
    echo -e "${RED}❌ Python 3.9+ is required (${PYVER})${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python OK${NC}"

# GLM Setup
echo -e "${BLUE}Checking GLM configuration...${NC}"
if [ -f "$SETUP_DIR/glm_setup.sh" ]; then
    echo -e "${YELLOW}⚠️  GLM configuration found. Setting up Claude Code + GLM integration...${NC}"
    if [ -z "$ANTHROPIC_BASE_URL" ] || [ -z "$ANTHROPIC_AUTH_TOKEN" ]; then
        echo -e "${YELLOW}⚠️  GLM environment variables not found. Running glm_setup.sh...${NC}"
        bash "$SETUP_DIR/glm_setup.sh"
        echo -e "${GREEN}✅ GLM configuration applied${NC}"
        echo -e "${YELLOW}⚠️  Please source ~/.bashrc or restart your terminal to apply GLM environment variables${NC}"
    else
        echo -e "${GREEN}✅ GLM environment variables already configured${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  glm_setup.sh not found in $SETUP_DIR. Skipping GLM setup.${NC}"
fi

# OpenSpec Installation
echo -e "${BLUE}Installing OpenSpec...${NC}"
if command -v npm &> /dev/null; then
    npm install -g @fission-ai/openspec@latest
    echo -e "${GREEN}✅ OpenSpec installed${NC}"
else
    echo -e "${YELLOW}⚠️  npm not found. Skipping OpenSpec installation.${NC}"
fi

# Virtualenv
echo -e "${BLUE}Setting up virtual environment...${NC}"
if [ "$FORCE_REBUILD" = true ] && [ -d "venv" ]; then
    echo "Recreating virtual environment..."
    rm -rf venv
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

PIP="$PROJECT_ROOT/venv/bin/pip"
PY="$PROJECT_ROOT/venv/bin/python"

# Upgrade pip and install Django + test deps
echo -e "${BLUE}Installing Django and dependencies...${NC}"
$PIP install --upgrade pip setuptools wheel
$PIP install "django>=4.2" pytest>=7.0.0
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Run Django migrations
echo -e "${BLUE}Applying Django migrations...${NC}"
if [ ! -d "runtime" ]; then
    echo -e "${YELLOW}⚠️  runtime/ not found. Ensure this repository contains a Django project in runtime/${NC}"
fi

if [ -f "runtime/manage.py" ]; then
    cd runtime || exit 1
    # Create migrations if needed and apply
    $PY manage.py makemigrations 2>/dev/null || true
    $PY manage.py migrate
    echo -e "${GREEN}✅ Migrations applied${NC}"

    # Create admin user (non-interactive if env vars present)
    echo -e "${BLUE}Setting up admin user...${NC}"
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
        export DJANGO_SUPERUSER_USERNAME DJANGO_SUPERUSER_EMAIL DJANGO_SUPERUSER_PASSWORD
        $PY manage.py createsuperuser --noinput || {
            echo -e "${YELLOW}⚠️  createsuperuser failed (may already exist)${NC}"
        }
    else
        echo -e "${YELLOW}⚠️  DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD not all set.${NC}"
        echo "Running interactive createsuperuser (you can set the env vars for non-interactive creation):"
        $PY manage.py createsuperuser || true
    fi
    cd ..
else
    echo -e "${YELLOW}⚠️  runtime/manage.py not found. Skipping migrations and admin setup.${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Host Django Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1) Start the application:"
echo -e "   ${YELLOW}cd runtime && ../venv/bin/python manage.py runserver 0.0.0.0:8000${NC}"
echo ""
echo "2) Access the application:"
echo "   • Application: http://localhost:8000/"
echo ""
echo "3) Run tests:"
echo -e "   ${YELLOW}../venv/bin/python -m pytest${NC}"
echo ""

exit 0