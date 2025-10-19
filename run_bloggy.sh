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
COMMAND="run"        # Default command

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
        --postgres|-p)
            USE_POSTGRES=true
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
        --setup|-s)
            COMMAND="setup"
            shift
            ;;
        --migrate|-m)
            COMMAND="migrate"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  (none)            Run the Django application (default)"
            echo "  --setup            Setup the application (install deps, migrations)"
            echo "  --migrate          Run database migrations only"
            echo ""
            echo "Options:"
            echo "  --local, -l        Run locally (default)"
            echo "  --docker, -d       Run with Docker"
            echo "  --postgres, -p     Use PostgreSQL (starts Docker container)"
            echo "  --background, -b   Run in background"
            echo "  --foreground, -f   Run in foreground"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run locally"
            echo "  $0 --postgres      # Run locally with PostgreSQL"
            echo "  $0 --setup         # Setup the application"
            echo "  $0 --migrate       # Run migrations only"
            echo "  $0 --docker        # Run with Docker"
            exit 0
            ;;
    esac
done

# Handle specific commands
if [ "$COMMAND" = "migrate" ]; then
    echo -e "${BLUE}🔄 Running database migrations only...${NC}"
    cd blogapp

    # Setup PostgreSQL if requested
    if [ "$USE_POSTGRES" = true ]; then
        echo -e "${BLUE}Starting PostgreSQL with Docker...${NC}"
        cd "$PROJECT_ROOT"

        if [ ! -f "docker-compose.yml" ]; then
            cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: django_blog_db
    environment:
      POSTGRES_DB: djangoblog
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
        fi

        docker compose up -d postgres
        sleep 5

        export DB_ENGINE='django.db.backends.postgresql'
        export DB_NAME='djangoblog'
        export DB_USER='postgres'
        export DB_PASSWORD='postgres'
        export DB_HOST='localhost'
        export DB_PORT='5432'

        cd blogapp
    fi

    python manage.py migrate
    echo -e "${GREEN}✅ Migrations completed successfully${NC}"
    exit 0
fi

if [ "$COMMAND" = "setup" ]; then
    echo -e "${BLUE}🔧 Setting up Django Blog Application...${NC}"
    echo ""

    # Setup virtual environment
    echo -e "${BLUE}Setting up Python environment...${NC}"
    if [ ! -d "venv" ]; then
        python -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${GREEN}✅ Virtual environment already exists${NC}"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo -e "${BLUE}Installing dependencies...${NC}"
    pip install --upgrade pip setuptools wheel
    pip install -r setup/requirements.txt
    pip install -r blogapp/requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"

    # Setup PostgreSQL if requested
    if [ "$USE_POSTGRES" = true ]; then
        echo -e "${BLUE}Starting PostgreSQL with Docker...${NC}"

        if [ ! -f "docker-compose.yml" ]; then
            cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: django_blog_db
    environment:
      POSTGRES_DB: djangoblog
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
        fi

        docker compose up -d postgres
        echo -e "${GREEN}✅ PostgreSQL started on port 5432${NC}"
        sleep 5

        # Update .env for PostgreSQL
        if [ -f "blogapp/.env" ]; then
            sed -i 's/DB_ENGINE=sqlite/DB_ENGINE=postgresql/' blogapp/.env
            sed -i 's/DB_NAME=db.sqlite3/DB_NAME=djangoblog/' blogapp/.env
            sed -i 's/DB_USER=.*/DB_USER=postgres/' blogapp/.env
            sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=postgres/' blogapp/.env
            sed -i 's/DB_HOST=.*/DB_HOST=localhost/' blogapp/.env
            sed -i 's/DB_PORT=.*/DB_PORT=5432/' blogapp/.env
        fi
    fi

    # Run migrations
    echo -e "${BLUE}Running database migrations...${NC}"
    cd blogapp
    python manage.py migrate
    echo -e "${GREEN}✅ Migrations applied successfully${NC}"

    # Create sample data
    echo -e "${BLUE}Creating sample data...${NC}"
    python create_sample_data.py
    echo -e "${GREEN}✅ Sample data created${NC}"

    # Collect static files
    echo -e "${BLUE}Collecting static files...${NC}"
    python manage.py collectstatic --noinput
    echo -e "${GREEN}✅ Static files collected${NC}"

    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run the application: ${BLUE}./run_bloggy.sh${NC}"
    echo "  2. Access at: ${GREEN}http://localhost:8000${NC}"
    echo "  3. Admin panel: ${GREEN}http://localhost:8000/admin${NC}"
    echo ""
    exit 0
fi

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

# Setup PostgreSQL with Docker if needed
if [ "$USE_POSTGRES" = true ]; then
    echo -e "${BLUE}Starting PostgreSQL with Docker...${NC}"
    cd "$PROJECT_ROOT"

    # Check if docker-compose.yml exists for PostgreSQL
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${BLUE}Creating docker-compose.yml for PostgreSQL...${NC}"
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: django_blog_db
    environment:
      POSTGRES_DB: djangoblog
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    fi

    # Start PostgreSQL
    docker compose up -d postgres
    echo -e "${GREEN}✅ PostgreSQL started on port 5432${NC}"

    # Wait for PostgreSQL to be ready
    echo -e "${BLUE}Waiting for PostgreSQL to be ready...${NC}"
    sleep 5

    # Update environment for PostgreSQL
    export DB_ENGINE='django.db.backends.postgresql'
    export DB_NAME='djangoblog'
    export DB_USER='postgres'
    export DB_PASSWORD='postgres'
    export DB_HOST='localhost'
    export DB_PORT='5432'

    cd blogapp
fi

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

