.PHONY: help build up down logs shell db-migrate db-backup db-info

# Default target
help:
	@echo "DjangoBase Development Commands"
	@echo ""
	@echo "Docker Commands:"
	@echo "  build      - Build all Docker images"
	@echo "  up         - Start all services in development mode"
	@echo "  up-prod    - Start all services in production mode"
	@echo "  down       - Stop all services"
	@echo "  logs       - Show logs for all services"
	@echo "  shell      - Open Django shell in container"
	@echo ""
	@echo "Database Commands:"
	@echo "  db-migrate - Run database migrations"
	@echo "  db-info    - Show database information"
	@echo "  db-stats   - Show database statistics"
	@echo "  db-backup  - Create database backup"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev-setup  - Initial development setup"
	@echo "  test       - Run tests"
	@echo "  clean      - Clean up Docker containers and images"

# Docker Commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Access the app at http://localhost:8000"
	@echo "pgAdmin available at http://localhost:5050 (admin@example.com / admin)"

up-dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development services started"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"
	@echo "pgAdmin: http://localhost:5050"

up-prod:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production services started"

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec web python manage.py shell

# Database Commands
db-migrate:
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

db-info:
	docker-compose exec web python manage.py db_ops info

db-stats:
	docker-compose exec web python manage.py db_ops stats

db-backup:
	docker-compose exec web python manage.py db_ops backup

db-setup:
	docker-compose exec web python manage.py db_ops setup

# Development Commands
dev-setup: up-dev
	sleep 5
	$(MAKE) db-migrate
	@echo "Creating superuser..."
	@docker-compose exec web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None"
	@echo ""
	@echo "Development setup complete!"
	@echo "Database: PostgreSQL on localhost:5432"
	@echo "Superuser: admin / admin123"
	@echo "Redis: localhost:6379"
	@echo "pgAdmin: http://localhost:5050 (admin@example.com / admin)"

test:
	docker-compose exec web python manage.py test

clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

# Production Commands
deploy-prod:
	docker-compose -f docker-compose.prod.yml build
	docker-compose -f docker-compose.prod.yml up -d

# Maintenance Commands
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose exec web python manage.py createsuperuser