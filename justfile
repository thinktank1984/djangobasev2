export COMPOSE_FILE := "docker/docker-compose.yaml"

## Just does not yet manage signals for subprocesses reliably, which can lead to unexpected behavior.
## Exercise caution before expanding its usage in production environments. 
## For more information, see https://github.com/casey/just/issues/2473 .


# Default command to list all available commands.
default:
    @just --list

# build: Build all images.
build:
    @echo "Building images..."
    @docker compose build

# build-runtime: Build only runtime image.
build-runtime:
    @echo "Building runtime image..."
    @docker compose build runtime

# up: Start all containers.
up:
    @echo "Starting all containers..."
    @docker compose up -d --remove-orphans

# runtime: Start runtime application in Docker (background, default) using run_bloggy.sh.
runtime:
    @./run_bloggy.sh

# runtime-fg: Start runtime in Docker (foreground) using run_bloggy.sh.
runtime-fg:
    @./run_bloggy.sh --foreground

# runtime-local: Start runtime locally with uv using run_bloggy.sh.
runtime-local:
    @./run_bloggy.sh --local

# runtime-rebuild: Force rebuild Docker image and start runtime.
runtime-rebuild:
    @echo "Forcing Docker rebuild..."
    @./setup/setup.sh --docker --rebuild
    @./run_bloggy.sh

# monitoring: Start monitoring stack (prometheus, grafana, alertmanager, cadvisor).
monitoring:
    @echo "Starting monitoring stack..."
    @docker compose up -d prometheus grafana alertmanager cadvisor

# down: Stop all containers.
down:
    @echo "Stopping containers..."
    @docker compose down

# restart: Restart containers.
restart *args:
    @echo "Restarting containers..."
    @docker compose restart {{args}}

# prune: Remove containers and their volumes.
prune *args:
    @echo "Killing containers and removing volumes..."
    @docker compose down -v {{args}}

# logs: View container logs
logs *args:
    @docker compose logs -f {{args}}

# runtime-logs: View runtime application logs
runtime-logs:
    @docker compose logs -f runtime

# shell: Open a bash shell in the runtime container.
shell:
    @docker compose exec runtime bash

# runtime-setup: Setup runtime application (create admin user).
runtime-setup:
    @echo "Setting up runtime application..."
    @docker compose exec runtime emmett setup

# runtime-migrate: Run runtime migrations.
runtime-migrate:
    @echo "Running migrations..."
    @docker compose exec runtime emmett migrations up

# runtime-test: Run runtime tests.
runtime-test:
    @echo "Running tests..."
    @docker compose exec runtime pytest integration_tests/ -v

# ps: Show running containers.
ps:
    @docker compose ps

# status: Show detailed container status.
status:
    @docker compose ps -a
