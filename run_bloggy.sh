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
USE_DOCKER=false     # Default to local mode for devcontainer
USE_POSTGRES=true    # Default to PostgreSQL in local mode
USE_BACKGROUND=true  # Default to background
COMMAND="run"        # Default to run application

for arg in "$@"; do
    case $arg in
        --local|-l)
            USE_DOCKER=false
            USE_POSTGRES=true  # PostgreSQL in local mode
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
        --run|-r)
            COMMAND="run"
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
        --build-only)
            COMMAND="build"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS] [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  (none)            Run the application (default)"
            echo "  --setup            Setup the application (install deps, migrations)"
            echo "  --run              Run the application only"
            echo "  --migrate          Run database migrations only"
            echo "  --build-only       Build Docker images only"
            echo ""
            echo "Options:"
            echo "  --local, -l        Run locally"
            echo "  --docker, -d       Use Docker (default)"
            echo "  --postgres, -p     Use PostgreSQL (starts Docker container)"
            echo "  --background, -b   Run in background"
            echo "  --foreground, -f   Run in foreground"
            echo "  --help, -h         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run application (default)"
            echo "  $0 --setup         # Setup the application"
            echo "  $0 --postgres      # Run with PostgreSQL"
            echo "  $0 --local         # Run locally"
            echo "  $0 --build-only    # Build Docker images only"
            exit 0
            ;;
    esac
done

# Function to check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
        echo ""
        echo -e "${BLUE}Please install Docker:${NC}"
        echo "  • Ubuntu/Debian: sudo apt-get install docker.io docker-compose"
        echo "  • macOS: Download Docker Desktop from docker.com"
        echo "  • Windows: Download Docker Desktop from docker.com"
        echo "  • Or follow: https://docs.docker.com/get-docker/"
        echo ""
        echo -e "${YELLOW}Alternative: Use local development mode:${NC}"
        echo "  ${BLUE}./run_bloggy.sh --local${NC}"
        return 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed${NC}"
        echo ""
        echo -e "${BLUE}Please install Docker Compose:${NC}"
        echo "  • Ubuntu/Debian: sudo apt-get install docker-compose"
        echo "  • Or follow: https://docs.docker.com/compose/install/"
        echo ""
        return 1
    fi

    return 0
}

# Function to check if Docker containers are built
check_docker_images() {
    echo -e "${BLUE}Checking Docker images...${NC}"

    # Check for Django app image
    if docker images | grep -q "django-blog-app"; then
        echo -e "${GREEN}✅ Django app image found${NC}"
        DJANGO_IMAGE_EXISTS=true
    else
        echo -e "${YELLOW}⚠️ Django app image not found${NC}"
        DJANGO_IMAGE_EXISTS=false
    fi

    # Check for PostgreSQL image
    if docker images | grep -q "postgres"; then
        echo -e "${GREEN}✅ PostgreSQL image found${NC}"
        POSTGRES_IMAGE_EXISTS=true
    else
        echo -e "${YELLOW}⚠️ PostgreSQL image not found${NC}"
        POSTGRES_IMAGE_EXISTS=false
    fi

    if [ "$DJANGO_IMAGE_EXISTS" = true ] && [ "$POSTGRES_IMAGE_EXISTS" = true ]; then
        return 0  # All images exist
    else
        return 1  # Some images missing
    fi
}

# Function to build Docker images
build_docker_images() {
    echo -e "${BLUE}🔨 Building Docker images...${NC}"

    # Check if Dockerfile exists
    if [ ! -f "runtime/Dockerfile" ]; then
        echo -e "${BLUE}Creating Dockerfile for Django application...${NC}"
        cat > runtime/Dockerfile << 'EOF'
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "core.wsgi:application"]
EOF
    fi

    # Check if docker-compose.yml exists
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${BLUE}Creating docker-compose.yml...${NC}"
        cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: django_blog_db
    environment:
      POSTGRES_DB: djangoblog
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build:
      context: ./runtime
      dockerfile: Dockerfile
    container_name: django_blog_app
    command: gunicorn --bind 0.0.0.0:8000 core.wsgi:application
    volumes:
      - ./runtime:/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    environment:
      - DB_ENGINE=django.db.backends.postgresql
      - DB_NAME=djangoblog
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_HOST=db
      - DB_PORT=5432
      - DEBUG=True
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    fi

    # Build images
    echo -e "${BLUE}Building Django application image...${NC}"
    docker compose build web

    # Pull PostgreSQL image
    echo -e "${BLUE}Pulling PostgreSQL image...${NC}"
    docker compose pull db

    echo -e "${GREEN}✅ Docker images built successfully${NC}"
}

# Function to run migrations
run_migrations() {
    echo -e "${BLUE}🔄 Running database migrations...${NC}"

    if [ "$USE_DOCKER" = true ]; then
        # Run migrations in Docker container
        echo -e "${BLUE}Running migrations in Docker container...${NC}"
        docker compose exec web python manage.py migrate

        echo -e "${BLUE}Creating sample data...${NC}"
        docker compose exec web python create_sample_data.py
    else
        # Local migrations
        cd runtime

        # Create logs directory for database logging
        echo -e "${BLUE}Creating logs directory...${NC}"
        mkdir -p logs
        echo -e "${GREEN}✅ Logs directory created${NC}"

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

            cd runtime
        fi

        # Run migrations for default database
        python manage.py migrate
        echo -e "${GREEN}✅ Default database migrations completed${NC}"

        # Run migrations for logs database
        echo -e "${BLUE}Running migrations for logs database...${NC}"
        python manage.py migrate --database=logs
        echo -e "${GREEN}✅ Logs database migrations completed${NC}"

        echo -e "${BLUE}Creating sample data...${NC}"
        python create_sample_data.py
    fi

    echo -e "${GREEN}✅ Migrations and sample data completed successfully${NC}"
}

# Handle specific commands
if [ "$COMMAND" = "migrate" ]; then
    echo -e "${BLUE}🔄 Running database migrations only...${NC}"
    run_migrations
    exit 0
fi

if [ "$COMMAND" = "build" ]; then
    echo -e "${BLUE}🔨 Building Docker images only...${NC}"
    if ! check_docker_images; then
        build_docker_images
    else
        echo -e "${GREEN}✅ All Docker images already exist${NC}"
    fi
    exit 0
fi

if [ "$COMMAND" = "setup" ]; then
    echo -e "${BLUE}🔧 Setting up Django Blog Application...${NC}"
    echo ""

    # Display requirements
    echo -e "${BLUE}📋 System Requirements:${NC}"
    echo "  • Docker Desktop or Docker Engine"
    echo "  • Docker Compose"
    echo "  • Python 3.9+ (for local development)"
    echo "  • Git"
    echo "  • At least 4GB RAM"
    echo "  • 2GB available disk space"
    echo ""

    echo -e "${BLUE}📦 What will be installed:${NC}"
    if [ "$USE_DOCKER" = true ]; then
        echo "  • Docker containers:"
        echo "    - Django Blog Application (Python 3.12)"
        echo "    - PostgreSQL 15 Database"
        echo "    - Redis (for caching/sessions)"
        echo "  • Docker images (~800MB total)"
        echo "  • Database volumes for data persistence"
    else
        echo "  • Python virtual environment"
        echo "  • Django and all dependencies"
        echo "  • PostgreSQL (if --postgres specified)"
    fi
    echo "  • Sample blog data (articles, categories, comments)"
    echo ""

    if [ "$USE_DOCKER" = true ]; then
        # Docker setup workflow
        echo -e "${BLUE}🐳 Docker Setup Workflow:${NC}"
        echo ""

        # Step 1: Check Docker images
        echo -e "${BLUE}Step 1: Checking existing Docker images...${NC}"
        if check_docker_images; then
            echo -e "${GREEN}✅ All required Docker images already exist${NC}"
        else
            echo -e "${YELLOW}⚠️ Some Docker images missing, will build them${NC}"
        fi
        echo ""

        # Step 2: Build Docker images
        echo -e "${BLUE}Step 2: Building Docker images...${NC}"
        if ! check_docker_images; then
            build_docker_images
        else
            echo -e "${GREEN}✅ Docker images already up to date${NC}"
        fi
        echo ""

        # Step 3: Start containers
        echo -e "${BLUE}Step 3: Starting Docker containers...${NC}"
        docker compose up -d
        echo -e "${GREEN}✅ Containers started${NC}"
        echo ""

        # Step 4: Wait for database
        echo -e "${BLUE}Step 4: Waiting for database to be ready...${NC}"
        sleep 10
        echo -e "${GREEN}✅ Database is ready${NC}"
        echo ""

        # Step 5: Run migrations
        echo -e "${BLUE}Step 5: Running database migrations...${NC}"
        run_migrations
        echo ""

        echo -e "${GREEN}🎉 Docker setup completed successfully!${NC}"
        echo ""
        echo "Application is running at:"
        echo "  • Blog: ${GREEN}http://localhost:8000${NC}"
        echo "  • Admin: ${GREEN}http://localhost:8000/admin${NC}"
        echo ""
        echo "Docker commands:"
        echo "  • View logs: ${BLUE}docker compose logs -f${NC}"
        echo "  • Stop: ${BLUE}docker compose down${NC}"
        echo "  • Restart: ${BLUE}docker compose restart${NC}"
        echo ""

    else
        # Local setup workflow
        echo -e "${BLUE}💻 Local Setup Workflow:${NC}"
        echo ""

        # Setup virtual environment (skip in devcontainer)
        if [ -n "$DEVCONTAINER" ] || [ -d ".devcontainer" ]; then
            echo -e "${BLUE}Step 1: Using devcontainer Python environment...${NC}"
            echo -e "${GREEN}✅ Dependencies already installed via devcontainer${NC}"
        else
            echo -e "${BLUE}Step 1: Setting up Python environment...${NC}"
            if [ ! -d "venv" ]; then
                python -m venv venv
                echo -e "${GREEN}✅ Virtual environment created${NC}"
            else
                echo -e "${GREEN}✅ Virtual environment already exists${NC}"
            fi

            # Activate virtual environment
            source venv/bin/activate
        fi

        # Install dependencies (skip in devcontainer)
        if [ -n "$DEVCONTAINER" ] || [ -d ".devcontainer" ]; then
            echo -e "${BLUE}Step 2: Dependencies already available in devcontainer...${NC}"
            echo -e "${GREEN}✅ Dependencies ready${NC}"
        else
            echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
            pip install --upgrade pip setuptools wheel
            pip install -r setup/requirements.txt
            pip install -r runtime/requirements.txt
            echo -e "${GREEN}✅ Dependencies installed${NC}"
        fi

        # Setup PostgreSQL if requested
        if [ "$USE_POSTGRES" = true ]; then
            echo -e "${BLUE}Step 3: Starting PostgreSQL with Docker...${NC}"
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
            if [ -f "runtime/.env" ]; then
                sed -i 's/DB_ENGINE=sqlite/DB_ENGINE=postgresql/' runtime/.env
                sed -i 's/DB_NAME=db.sqlite3/DB_NAME=djangoblog/' runtime/.env
                sed -i 's/DB_USER=.*/DB_USER=postgres/' runtime/.env
                sed -i 's/DB_PASSWORD=.*/DB_PASSWORD=postgres/' runtime/.env
                sed -i 's/DB_HOST=.*/DB_HOST=localhost/' runtime/.env
                sed -i 's/DB_PORT=.*/DB_PORT=5432/' runtime/.env
            fi
        fi

        # Run migrations and setup
        echo -e "${BLUE}Step 4: Creating logs directory...${NC}"
        cd runtime
        mkdir -p logs
        echo -e "${GREEN}✅ Logs directory created${NC}"

        echo -e "${BLUE}Step 5: Running database migrations...${NC}"
        python manage.py migrate
        echo -e "${GREEN}✅ Default database migrations completed${NC}"

        echo -e "${BLUE}Step 6: Running logs database migrations...${NC}"
        python manage.py migrate --database=logs
        echo -e "${GREEN}✅ Logs database migrations completed${NC}"

        # Create sample data
        echo -e "${BLUE}Step 7: Creating sample data...${NC}"
        python create_sample_data.py
        echo -e "${GREEN}✅ Sample data created${NC}"

        # Collect static files
        echo -e "${BLUE}Step 8: Collecting static files...${NC}"
        python manage.py collectstatic --noinput
        echo -e "${GREEN}✅ Static files collected${NC}"

        echo ""
        echo -e "${GREEN}🎉 Local setup completed successfully!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Run the application: ${BLUE}./run_bloggy.sh --run${NC}"
        echo "  2. Access at: ${GREEN}http://localhost:8000${NC}"
        echo "  3. Admin panel: ${GREEN}http://localhost:8000/admin${NC}"
        echo ""
    fi
    exit 0
fi

if [ "$COMMAND" = "run" ]; then
    echo -e "${BLUE}🚀 Running Django Blog Application...${NC}"
    echo ""

    if [ "$USE_DOCKER" = true ]; then
        # Docker run workflow
        echo -e "${BLUE}🐳 Starting Docker containers...${NC}"

        # Check if containers exist
        if ! docker ps --format "table {{.Names}}" | grep -q "django_blog_app"; then
            echo -e "${YELLOW}⚠️ Containers not running, starting them...${NC}"
            docker compose up -d
            sleep 5
        fi

        echo -e "${GREEN}✅ Application is running at:${NC}"
        echo "  • Blog: ${GREEN}http://localhost:8000${NC}"
        echo "  • Admin: ${GREEN}http://localhost:8000/admin${NC}"
        echo ""
        echo "Docker commands:"
        echo "  • View logs: ${BLUE}docker compose logs -f${NC}"
        echo "  • Stop: ${BLUE}docker compose down${NC}"
        echo "  • Restart: ${BLUE}docker compose restart${NC}"
        echo ""

    else
        # Local run workflow
        echo -e "${BLUE}💻 Starting local development server...${NC}"
        cd runtime

        # Check if virtual environment exists (skip in devcontainer)
        if [ -n "$DEVCONTAINER" ] || [ -d "../.devcontainer" ]; then
            echo -e "${GREEN}✅ Using devcontainer Python environment${NC}"
        else
            if [ ! -d "../venv" ]; then
                echo -e "${RED}❌ Virtual environment not found. Run './run_bloggy.sh --setup' first.${NC}"
                exit 1
            fi

            # Activate virtual environment
            source ../venv/bin/activate
        fi

        # Check if database exists
        if [ ! -f "db.sqlite3" ] && [ "$USE_POSTGRES" != true ]; then
            echo -e "${YELLOW}⚠️ Database not found. Running migrations...${NC}"
            python manage.py migrate
            python create_sample_data.py
        fi

        echo -e "${GREEN}✅ Starting development server...${NC}"
        echo "Application will be available at:"
        echo "  • Blog: ${GREEN}http://localhost:8000${NC}"
        echo "  • Admin: ${GREEN}http://localhost:8000/admin${NC}"
        echo ""
        echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
        echo ""

        # Kill any existing Django processes on port 8000
        echo -e "${YELLOW}🔄 Checking for existing Django processes...${NC}"
        DJANGO_PIDS=$(ps aux | grep "python manage.py runserver" | grep -v grep | awk '{print $2}')
        if [ -n "$DJANGO_PIDS" ]; then
            echo -e "${YELLOW}   Found Django processes, stopping them...${NC}"
            echo "$DJANGO_PIDS" | xargs kill -9 2>/dev/null || true
            sleep 2
        fi

        # Start the Django development server
        echo -e "${GREEN}🚀 Starting Django development server...${NC}"
        python manage.py runserver 0.0.0.0:8000
    fi
    exit 0
fi

# Default behavior (no command specified) - run setup workflow
echo -e "${BLUE}🔧 Default Setup: Building and starting Django Blog Application...${NC}"
echo ""

# Check Docker availability first
if ! check_docker; then
    echo -e "${RED}❌ Cannot proceed with Docker setup${NC}"
    echo -e "${YELLOW}💡 Falling back to local development mode${NC}"
    echo ""

    # Switch to local setup
    USE_DOCKER=false
    COMMAND="setup"

    # Run local setup
    echo -e "${BLUE}💻 Local Setup Workflow:${NC}"
    echo ""

    # Setup virtual environment (skip in devcontainer)
    if [ -n "$DEVCONTAINER" ] || [ -d ".devcontainer" ]; then
        echo -e "${BLUE}Step 1: Using devcontainer Python environment...${NC}"
        echo -e "${GREEN}✅ Dependencies already installed via devcontainer${NC}"
    else
        echo -e "${BLUE}Step 1: Setting up Python environment...${NC}"
        if [ ! -d "venv" ]; then
            python -m venv venv
            echo -e "${GREEN}✅ Virtual environment created${NC}"
        else
            echo -e "${GREEN}✅ Virtual environment already exists${NC}"
        fi

        # Activate virtual environment
        source venv/bin/activate
    fi

    # Install dependencies (skip in devcontainer)
    if [ -n "$DEVCONTAINER" ] || [ -d ".devcontainer" ]; then
        echo -e "${BLUE}Step 2: Dependencies already available in devcontainer...${NC}"
        echo -e "${GREEN}✅ Dependencies ready${NC}"
    else
        echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
        pip install --upgrade pip setuptools wheel
        pip install -r setup/requirements.txt
        pip install -r runtime/requirements.txt
        echo -e "${GREEN}✅ Dependencies installed${NC}"
    fi

    # Run migrations and setup
    echo -e "${BLUE}Step 3: Creating logs directory...${NC}"
    cd runtime
    mkdir -p logs
    echo -e "${GREEN}✅ Logs directory created${NC}"

    echo -e "${BLUE}Step 4: Running database migrations...${NC}"
    python manage.py migrate
    echo -e "${GREEN}✅ Default database migrations completed${NC}"

    echo -e "${BLUE}Step 5: Running logs database migrations...${NC}"
    python manage.py migrate --database=logs
    echo -e "${GREEN}✅ Logs database migrations completed${NC}"

    # Create sample data
    echo -e "${BLUE}Step 6: Creating sample data...${NC}"
    python create_sample_data.py
    echo -e "${GREEN}✅ Sample data created${NC}"

    # Collect static files
    echo -e "${BLUE}Step 7: Collecting static files...${NC}"
    python manage.py collectstatic --noinput
    echo -e "${GREEN}✅ Static files collected${NC}"

    echo ""
    echo -e "${GREEN}🎉 Local setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run the application: ${BLUE}./run_bloggy.sh --run${NC}"
    echo "  2. Access at: ${GREEN}http://localhost:8000${NC}"
    echo "  3. Admin panel: ${GREEN}http://localhost:8000/admin${NC}"
    echo ""
    exit 0
fi

# Docker is available, proceed with Docker setup
echo -e "${BLUE}📋 System Requirements:${NC}"
echo "  ✅ Docker Desktop or Docker Engine (Found)"
echo "  ✅ Docker Compose (Found)"
echo "  • Python 3.9+ (for local development)"
echo "  • Git"
echo "  • At least 4GB RAM"
echo "  • 2GB available disk space"
echo ""

echo -e "${BLUE}📦 What will be installed:${NC}"
echo "  • Docker containers:"
echo "    - Django Blog Application (Python 3.12)"
echo "    - PostgreSQL 15 Database"
echo "  • Docker images (~800MB total)"
echo "  • Database volumes for data persistence"
echo "  • Sample blog data (articles, categories, comments)"
echo ""

echo -e "${BLUE}🐳 Docker Setup Workflow:${NC}"
echo ""

# Step 1: Check Docker images
echo -e "${BLUE}Step 1: Checking existing Docker images...${NC}"
if check_docker_images; then
    echo -e "${GREEN}✅ All required Docker images already exist${NC}"
else
    echo -e "${YELLOW}⚠️ Some Docker images missing, will build them${NC}"
fi
echo ""

# Step 2: Build Docker images
echo -e "${BLUE}Step 2: Building Docker images...${NC}"
if ! check_docker_images; then
    build_docker_images
else
    echo -e "${GREEN}✅ Docker images already up to date${NC}"
fi
echo ""

# Step 3: Start containers
echo -e "${BLUE}Step 3: Starting Docker containers...${NC}"
docker compose up -d
echo -e "${GREEN}✅ Containers started${NC}"
echo ""

# Step 4: Wait for database
echo -e "${BLUE}Step 4: Waiting for database to be ready...${NC}"
sleep 10
echo -e "${GREEN}✅ Database is ready${NC}"
echo ""

# Step 5: Run migrations
echo -e "${BLUE}Step 5: Running database migrations...${NC}"
run_migrations
echo ""

echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo ""
echo "Application is running at:"
echo "  • Blog: ${GREEN}http://localhost:8000${NC}"
echo "  • Admin: ${GREEN}http://localhost:8000/admin${NC}"
echo ""
echo "Docker commands:"
echo "  • View logs: ${BLUE}docker compose logs -f${NC}"
echo "  • Stop: ${BLUE}docker compose down${NC}"
echo "  • Restart: ${BLUE}docker compose restart${NC}"
echo ""

