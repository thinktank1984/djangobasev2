#!/bin/bash
# ---------------------------------------------------------------------------
# tasks_queue_setup.sh : Setup script for Agents Tasks Queue
#
# Features:
#   ✅ PostgreSQL 18 auto-install in .pgbin/.pgdata
#   ✅ Virtualenv auto-setup (.pgqvenv)
#   ✅ Configuration file creation
#   ✅ Directory structure setup
#   ✅ Dependencies installation
#   ✅ Quick start examples
# ---------------------------------------------------------------------------

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

say() { echo -e "${BLUE}[TASKS_QUEUE_SETUP]${NC} $*"; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $*${NC}"; }
error() { echo -e "${RED}❌ $*${NC}"; }

# Configuration
PG_VER=18.0
PG_BASEURL="https://ftp.postgresql.org/pub/source/v${PG_VER}/postgresql-${PG_VER}.tar.gz"
PG_SRC="postgresql-${PG_VER}"
PG_PREFIX="$(pwd)/.pgbin"
PGDATA="$(pwd)/.pgdata"
VENV=".pgqvenv"
PY_PKGS="pgqueuer asyncpg typer croniter"

# ---------------------------------------------------------------------------
# Header and introduction
# ---------------------------------------------------------------------------
echo -e "${BLUE}"
echo "=================================================="
echo "    Agents Tasks Queue Setup Script v2.0"
echo "    PostgreSQL 18 + PGQ-Cmd Scheduler"
echo "=================================================="
echo -e "${NC}"

say "Starting setup of Agents Tasks Queue with PostgreSQL ${PG_VER}..."

# ---------------------------------------------------------------------------
# System requirements check
# ---------------------------------------------------------------------------
say "Checking system requirements..."

# Check for required commands
for cmd in curl tar python3 make gcc; do
    if ! command -v "$cmd" &> /dev/null; then
        error "Required command '$cmd' not found. Please install it first."
        exit 1
    fi
done
success "All required commands are available"

# Check available disk space (need at least 2GB for PostgreSQL build)
available_space=$(df . | tail -1 | awk '{print $4}')
required_space=$((2 * 1024 * 1024)) # 2GB in KB

if [ "$available_space" -lt "$required_space" ]; then
    warning "Low disk space detected. PostgreSQL build requires at least 2GB."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        say "Setup cancelled."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Directory structure setup
# ---------------------------------------------------------------------------
say "Setting up directory structure..."

# Create necessary directories
mkdir -p logs
mkdir -p examples
mkdir -p scripts

success "Directory structure created"

# ---------------------------------------------------------------------------
# Configuration file setup
# ---------------------------------------------------------------------------
say "Setting up configuration files..."

# Create or update config.json
if [ ! -f "config.json" ]; then
    cat > config.json << EOF
{
  "log_dir": "logs",
  "pipeline": ["tee", "-a", "logs/pgq.log"],
  "pg_port": 5544,
  "max_connections": 100,
  "shared_buffers": "256MB",
  "effective_cache_size": "1GB"
}
EOF
    success "Created default config.json"
else
    success "config.json already exists"
fi

# ---------------------------------------------------------------------------
# Ensure PostgreSQL binaries exist
# ---------------------------------------------------------------------------
if [ ! -x "$PG_PREFIX/bin/postgres" ]; then
    say "Installing local PostgreSQL ${PG_VER}..."

    # Download PostgreSQL source
    say "Downloading PostgreSQL ${PG_VER} source code..."
    if ! curl -L "$PG_BASEURL" | tar xz; then
        error "Failed to download PostgreSQL source"
        exit 1
    fi

    # Build PostgreSQL
    say "Building PostgreSQL (this may take 10-20 minutes)..."
    cd "$PG_SRC"

    # Configure with minimal dependencies for faster build
    ./configure \
        --prefix="$PG_PREFIX" \
        --without-readline \
        --without-zlib \
        --without-openssl \
        --disable-nls \
        --enable-thread-safety \
        --with-libxml \
        --with-libxslt

    # Build and install
    if ! make -j$(nproc) && make install; then
        error "PostgreSQL build failed"
        cd ..
        rm -rf "$PG_SRC"
        exit 1
    fi

    cd ..
    rm -rf "$PG_SRC"
    success "PostgreSQL ${PG_VER} built and installed to $PG_PREFIX"
else
    success "PostgreSQL ${PG_VER} already installed"
fi

# ---------------------------------------------------------------------------
# Ensure database cluster
# ---------------------------------------------------------------------------
if [ ! -d "$PGDATA/base" ]; then
    say "Initializing PostgreSQL database cluster..."
    "$PG_PREFIX/bin/initdb" -D "$PGDATA" -A trust --encoding=UTF8 --locale=C
    success "Database cluster initialized"
else
    success "Database cluster already exists"
fi

# ---------------------------------------------------------------------------
# Configure PostgreSQL for pgq-cmd
# ---------------------------------------------------------------------------
say "Configuring PostgreSQL..."

# Create postgresql.conf if it doesn't exist
if [ ! -f "$PGDATA/postgresql.conf" ]; then
    cat > "$PGDATA/postgresql.conf" << EOF
# PostgreSQL configuration for pgq-cmd
port = 5544
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_min_duration_statement = 1000
EOF
else
    # Update port in existing configuration
    if ! grep -q "port = 5544" "$PGDATA/postgresql.conf"; then
        echo "port = 5544" >> "$PGDATA/postgresql.conf"
    fi
fi

success "PostgreSQL configured"

# ---------------------------------------------------------------------------
# Start PostgreSQL if not running
# ---------------------------------------------------------------------------
if ! "$PG_PREFIX/bin/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; then
    say "Starting PostgreSQL server..."
    "$PG_PREFIX/bin/pg_ctl" -D "$PGDATA" -l "$PGDATA/server.log" start

    # Wait for PostgreSQL to start
    sleep 3

    # Check if PostgreSQL started successfully
    if "$PG_PREFIX/bin/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; then
        success "PostgreSQL server started successfully"
    else
        error "PostgreSQL server failed to start. Check $PGDATA/server.log"
        exit 1
    fi
else
    success "PostgreSQL server already running"
fi

# ---------------------------------------------------------------------------
# Ensure Python environment
# ---------------------------------------------------------------------------
if [ ! -d "$VENV" ]; then
    say "Setting up Python virtual environment..."
    python3 -m venv "$VENV"
    . "$VENV/bin/activate"

    say "Installing Python packages..."
    pip install -qU pip
    pip install -qU $PY_PKGS

    success "Python environment setup complete"
else
    say "Python virtual environment already exists"
    . "$VENV/bin/activate"

    # Check if required packages are installed
    missing_packages=()
    for package in $PY_PKGS; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=($package)
        fi
    done

    if [ ${#missing_packages[@]} -gt 0 ]; then
        say "Installing missing Python packages: ${missing_packages[*]}"
        pip install -qU ${missing_packages[@]}
    fi

    success "Python environment ready"
fi

# ---------------------------------------------------------------------------
# Test database connection
# ---------------------------------------------------------------------------
say "Testing database connection..."

# Wait a moment for PostgreSQL to be fully ready
sleep 2

if python3 -c "
import asyncpg
import asyncio

async def test():
    try:
        conn = await asyncpg.connect('postgresql://localhost:5544/postgres')
        await conn.execute('SELECT 1')
        await conn.close()
        print('✅ Database connection successful')
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

result = asyncio.run(test())
exit(0 if result else 1)
"; then
    success "Database connection test passed"
else
    warning "Database connection test failed, but setup will continue"
fi

# ---------------------------------------------------------------------------
# Create example scripts
# ---------------------------------------------------------------------------
say "Creating example scripts..."

# Enhanced heartbeat script
cat > examples/heartbeat.sh << 'EOF'
#!/bin/bash
echo "=== System Heartbeat ==="
echo "Timestamp: $(date)"
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime)"
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h . | tail -1
echo ""
echo "PostgreSQL Processes:"
pgrep -fl postgres || echo "No PostgreSQL processes found"
echo "=== End Heartbeat ==="
EOF

# Database maintenance script
cat > examples/db_maintenance.sh << 'EOF'
#!/bin/bash
echo "=== Database Maintenance ==="
echo "Timestamp: $(date)"

# Check if PostgreSQL is running
if pgrep -f postgres > /dev/null; then
    echo "✅ PostgreSQL is running"

    # Try to connect and check database
    if command -v psql >/dev/null 2>&1; then
        echo "Database connections:"
        psql -h localhost -p 5544 -U postgres -d postgres -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "Could not connect to database"
    fi
else
    echo "❌ PostgreSQL is not running"
fi
echo "=== End Maintenance ==="
EOF

# Make scripts executable
chmod +x examples/heartbeat.sh
chmod +x examples/db_maintenance.sh

success "Example scripts created"

# ---------------------------------------------------------------------------
# Create quick start guide
# ---------------------------------------------------------------------------
say "Creating quick start guide..."

cat > QUICKSTART.md << 'EOF'
# Agents Tasks Queue - Quick Start Guide

## 🚀 Get Started Immediately

```bash
# 1. Start the task queue worker
./pgq-cmd run

# 2. In another terminal, schedule tasks:
./pgq-cmd schedule "*/5 * * * *" --name heartbeat -- ./examples/heartbeat.sh
./pgq-cmd schedule "0 2 * * *" --name db-maintenance -- ./examples/db_maintenance.sh

# 3. List scheduled tasks
./pgq-cmd list

# 4. Run immediate tasks
./pgq-cmd enqueue --name test -- echo "Hello from Tasks Queue!"
```

## 📊 Monitor Tasks

```bash
# View logs
tail -f logs/pgq.log

# List all scheduled tasks
./pgq-cmd list

# Check PostgreSQL status
.pgbin/bin/pg_ctl -D .pgdata status
```

## 🛠️ Configuration

Edit `config.json` to customize:
- Log directory and pipeline
- PostgreSQL port
- Database parameters

## 📚 Documentation

- Full documentation: `pgq-cmd-tasks-queue.md`
- Implementation details: `README-PGQ.md`
- Main README: `README.md`
EOF

success "Quick start guide created"

# ---------------------------------------------------------------------------
# Final validation
# ---------------------------------------------------------------------------
say "Running final validation..."

# Check all critical components
validation_passed=true

if [ ! -x "./pgq-cmd" ]; then
    error "pgq-cmd script not found or not executable"
    validation_passed=false
fi

if [ ! -f "./config.json" ]; then
    error "config.json not found"
    validation_passed=false
fi

if [ ! -d "./logs" ]; then
    error "logs directory not found"
    validation_passed=false
fi

if ! "$PG_PREFIX/bin/pg_ctl" -D "$PGDATA" status >/dev/null 2>&1; then
    error "PostgreSQL server is not running"
    validation_passed=false
fi

if [ "$validation_passed" = true ]; then
    success "All validation checks passed!"
else
    error "Some validation checks failed"
    exit 1
fi

# ---------------------------------------------------------------------------
# Success message
# ---------------------------------------------------------------------------
echo ""
echo -e "${GREEN}=================================================="
echo "    🎉 SETUP COMPLETED SUCCESSFULLY!"
echo "=================================================="
echo -e "${NC}"

echo -e "${BLUE}Your Agents Tasks Queue is ready with:${NC}"
echo -e "  • PostgreSQL ${PG_VER} server"
echo -e "  • Python virtual environment"
echo -e "  • PGQ-Cmd task scheduler"
echo -e "  • Example scripts"
echo -e "  • Configuration files"
echo ""

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Start the worker: ${BLUE}./pgq-cmd run${NC}"
echo -e "2. Schedule tasks: ${BLUE}./pgq-cmd schedule \"*/5 * * * *\" --name test -- echo \"Hello\"${NC}"
echo -e "3. Monitor: ${BLUE}./pgq-cmd list${NC}"
echo -e "4. Read: ${BLUE}cat QUICKSTART.md${NC}"
echo ""

echo -e "${GREEN}Happy task scheduling! 🚀${NC}"
echo ""

# PostgreSQL connection info
echo -e "${BLUE}PostgreSQL Connection Info:${NC}"
echo -e "  • Host: localhost"
echo -e "  • Port: 5544"
echo -e "  • Database: postgres"
echo -e "  • User: postgres"
echo -e "  • No password required (trust authentication)"
echo ""