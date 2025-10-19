# DjangoBase Project Setup Guide

This guide will help you set up the DjangoBase project with PostgreSQL and Redis using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Git
- Make (optional, but recommended for easy commands)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd djangobasev2

# Copy environment file
cp blogapp/.env.example .env

# Start development services (PostgreSQL + Redis + pgAdmin)
make up-dev

# Initial setup (migrations, superuser, etc.)
make dev-setup
```

### 2. Access the Application

- **Django App**: http://localhost:8000
- **pgAdmin**: http://localhost:5050
  - Email: admin@example.com
  - Password: admin
- **PostgreSQL**: localhost:5432
  - Database: djangobase
  - User: postgres
  - Password: postgres
- **Redis**: localhost:6379

### 3. Default Credentials

- **Django Superuser**: admin / admin123
- **PostgreSQL**: postgres / postgres
- **pgAdmin**: admin@example.com / admin

## Detailed Setup

### Docker Services

The project includes multiple Docker Compose configurations:

#### Development (`docker-compose.dev.yml`)
- PostgreSQL 15
- Redis 7
- pgAdmin (database management)

#### Production (`docker-compose.prod.yml`)
- PostgreSQL 15
- Redis 7 (with password)
- Django Web App (Gunicorn)
- Django Channels (Daphne)
- Nginx (reverse proxy)

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=djangobase
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration (for Channels)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Stripe Configuration (optional)
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID=

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://yourdomain.com
```

### Development Workflow

#### Common Commands

```bash
# Start services
make up-dev

# Stop services
make down

# View logs
make logs

# Open Django shell
make shell

# Run migrations
make db-migrate

# Create superuser
make createsuperuser

# Run tests
make test

# Database operations
make db-info      # Show database info
make db-stats     # Show database statistics
make db-backup    # Create backup
```

#### Manual Docker Commands

```bash
# Start services manually
docker-compose -f docker-compose.dev.yml up -d

# Run migrations manually
docker-compose exec web python manage.py migrate

# Create superuser manually
docker-compose exec web python manage.py createsuperuser

# Access database directly
docker-compose exec db psql -U postgres -d djangobase

# Access Redis directly
docker-compose exec redis redis-cli
```

### Database Management

#### Using Management Commands

```bash
# Database information
docker-compose exec web python manage.py db_ops info

# Database statistics
docker-compose exec web python manage.py db_ops stats

# Create backup
docker-compose exec web python manage.py db_ops backup

# Restore backup
docker-compose exec web python manage.py db_ops restore /path/to/backup.dump

# Execute custom query
docker-compose exec web python manage.py db_ops query "SELECT COUNT(*) FROM auth_user"

# Optimize tables
docker-compose exec web python manage.py db_ops optimize
```

#### Using pgAdmin

1. Open http://localhost:5050
2. Login with admin@example.com / admin
3. Add new server:
   - Host: db
   - Port: 5432
   - Username: postgres
   - Password: postgres
   - Database: djangobase

### Real-time Features

The project includes real-time features using Django Channels and Redis:

#### WebSocket Endpoints

- `/ws/dashboard/` - Real-time dashboard updates
- `/ws/notifications/` - Push notifications
- `/ws/subscriptions/` - Subscription updates
- `/ws/presence/` - User presence tracking

#### Testing WebSocket Features

```bash
# Send test notifications
docker-compose exec web python manage.py test_websocket --user admin --type notification

# Send test dashboard updates
docker-compose exec web python manage.py test_websocket --user admin --type dashboard
```

### Production Deployment

#### Environment Setup

```bash
# Create production environment file
cp .env .env.prod

# Update production settings
# - Set DEBUG=False
# - Update SECRET_KEY
# - Set ALLOWED_HOSTS
# - Configure email backend
# - Set Stripe keys
```

#### Docker Compose Production

```bash
# Build and start production services
make up-prod

# Or manually
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

#### SSL Configuration

For production, update the `.env.prod` file:

```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### Troubleshooting

#### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps

   # Restart database service
   docker-compose restart db

   # Check database logs
   docker-compose logs db
   ```

2. **Migration Issues**
   ```bash
   # Reset migrations (development only)
   docker-compose exec web python manage.py migrate app_name zero
   docker-compose exec web python manage.py makemigrations app_name
   docker-compose exec web python manage.py migrate
   ```

3. **Static Files Not Loading**
   ```bash
   # Collect static files
   docker-compose exec web python manage.py collectstatic --noinput

   # Check static volume
   docker-compose exec web ls -la staticfiles/
   ```

4. **Redis Connection Issues**
   ```bash
   # Check Redis status
   docker-compose exec redis redis-cli ping

   # Restart Redis
   docker-compose restart redis
   ```

#### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

#### Database Access

```bash
# Access PostgreSQL
docker-compose exec db psql -U postgres -d djangobase

# Access Redis
docker-compose exec redis redis-cli

# Export database
docker-compose exec db pg_dump -U postgres djangobase > backup.sql

# Import database
docker-compose exec -T db psql -U postgres djangobase < backup.sql
```

### Development Tips

#### Code Quality

```bash
# Run tests
docker-compose exec web python manage.py test

# Check for migrations
docker-compose exec web python manage.py makemigrations --dry-run

# Collect static files
docker-compose exec web python manage.py collectstatic --dry-run
```

#### Performance

- Use persistent database connections (CONN_MAX_AGE)
- Optimize database queries with select_related/prefetch_related
- Use Redis for caching
- Monitor database performance with `make db-stats`

#### Security

- Use strong secrets in production
- Keep dependencies updated
- Use HTTPS in production
- Regularly backup database: `make db-backup`

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs: `make logs`
3. Check database health: `make db-info`
4. Run tests: `make test`

## Next Steps

After setup:

1. **Customize the application**: Modify models, views, and templates
2. **Add real-time features**: Implement WebSocket consumers
3. **Set up CI/CD**: Configure automated testing and deployment
4. **Monitor performance**: Use database statistics and logging
5. **Scale the application**: Use multiple containers and load balancers