# PostgreSQL Integration Documentation

This document provides comprehensive guidance for integrating PostgreSQL with the Django project, including query commands, database management, and optimization strategies.

## Overview

This Django project currently uses SQLite3 for development but is configured to support PostgreSQL for production environments. The PostgreSQL integration provides enhanced performance, concurrency, and scalability for production deployments.

## Database Configuration

### Current Setup

The project is configured to use PostgreSQL by default for both development and production:

```python
# core/settings.py
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'djangobase'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 60,  # Persistent connections
    }
}
```

### Docker Database Management

#### Makefile Commands
The project includes a Makefile with useful database commands:

```bash
# Database information
make db-info

# Database statistics
make db-stats

# Create backup
make db-backup

# Run migrations
make db-migrate

# Database setup for Docker
make db-setup
```

#### Management Commands
Django management commands for database operations:

```bash
# Show database information
python manage.py db_ops info

# Show database statistics
python manage.py db_ops stats

# Create backup
python manage.py db_ops backup --path /path/to/backup.dump

# Restore from backup
python manage.py db_ops restore /path/to/backup.dump

# Check database health
python manage.py db_ops health

# Execute custom query
python manage.py db_ops query "SELECT COUNT(*) FROM auth_user"

# Optimize tables
python manage.py db_ops optimize --table auth_user
```

### Environment Variables

Configure the following environment variables in your `.env` file:

```bash
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
```

### Environment Variables

Configure the following environment variables in your `.env` file:

```bash
# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

## Installation & Setup

This project uses Docker for PostgreSQL development and deployment. Docker provides a consistent environment across different machines and simplifies database management.

### Docker Setup (Recommended)

#### Quick Start with Docker
```bash
# Clone the repository
git clone <repository-url>
cd djangobasev2

# Start development services (PostgreSQL + Redis + pgAdmin)
make up-dev

# Initial setup (migrations, superuser, etc.)
make dev-setup
```

#### Manual Docker Commands
```bash
# Start only database services
docker-compose -f docker-compose.dev.yml up -d

# Run migrations
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

### Production Docker Setup
```bash
# Build and start production services
make up-prod

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### Local PostgreSQL Installation (Alternative)

If you prefer to run PostgreSQL locally instead of using Docker:

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS (using Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

#### Windows
Download and install PostgreSQL from the official website: https://www.postgresql.org/download/windows/

### 2. Database Setup

#### Create Database and User
```sql
-- Connect to PostgreSQL
sudo -u postgres psql

-- Create database
CREATE DATABASE your_db_name;

-- Create user with password
CREATE USER your_db_user WITH PASSWORD 'your_db_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;

-- Exit
\q
```

#### Alternative using createdb
```bash
# Create database
createdb -O your_db_user your_db_name

# Connect to database
psql -h localhost -U your_db_user -d your_db_name
```

### 3. Python Dependencies

Install the PostgreSQL adapter for Python:

```bash
# Add to requirements.txt
psycopg2-binary==2.9.9
# OR for better performance (requires PostgreSQL development headers)
psycopg2==2.9.9

# Install via pip
pip install psycopg2-binary
```

## Database Models

### Current Models Structure

The project includes several models that will be migrated to PostgreSQL:

#### User-related Models
- **User** (Django's built-in User model)
- **UserSettings** (app: dashboard)
- **UserPresence** (app: notifications)

#### Subscription Models
- **SubscriptionPlan** (app: subscriptions)
- **StripeCustomer** (app: subscriptions)

#### Notification Models
- **Notification** (app: notifications)

### Model Relationships

```python
# User relationships
User -> UserSettings (OneToOne)
User -> StripeCustomer (OneToOne)
User -> Notification (OneToMany)
User -> UserPresence (OneToOne)

# Subscription relationships
User -> SubscriptionPlan (ForeignKey via UserSettings)
User -> StripeCustomer (OneToOne)
```

## Migration Process

### 1. Backup Existing Data (if any)

```bash
# SQLite backup
python manage.py dumpdata > sqlite_backup.json

# Alternative using sqlite3 command
sqlite3 db.sqlite3 .dump > sqlite_backup.sql
```

### 2. Install Dependencies

```bash
pip install psycopg2-binary
```

### 3. Update Configuration

Update `core/settings.py` and `.env` file with PostgreSQL credentials.

### 4. Create Migrations

```bash
# Create migrations for all apps
python manage.py makemigrations

# Apply migrations to PostgreSQL database
python manage.py migrate
```

### 5. Load Data (if migrating from SQLite)

```bash
# Load data from backup
python manage.py loaddata sqlite_backup.json
```

## PostgreSQL Query Commands

### Basic Database Operations

#### Connect to Database
```bash
# Using psql
psql -h localhost -U your_db_user -d your_db_name

# Alternative with connection string
psql postgresql://your_db_user:your_db_password@localhost:5432/your_db_name
```

#### Database Information
```sql
-- List all databases
\l

-- Connect to specific database
\c your_db_name

-- List all tables
\dt

-- Describe table structure
\d table_name

-- List all users
\du

-- Show current user
\conninfo
```

### Django ORM Query Examples

#### Basic Queries
```python
from django.contrib.auth import get_user_model
from apps.subscriptions.models import SubscriptionPlan, StripeCustomer
from apps.notifications.models import Notification

User = get_user_model()

# Get all users
users = User.objects.all()

# Get active users
active_users = User.objects.filter(is_active=True)

# Get users with specific settings
users_with_premium = User.objects.filter(
    settings__subscription_plan__name='Premium'
)

# Count notifications per user
notification_counts = User.objects.annotate(
    notification_count=models.Count('notifications')
)
```

#### Advanced Queries
```python
from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone

# Users with active subscriptions
active_subscribers = User.objects.filter(
    settings__subscription_status='active',
    settings__subscription_end_date__gt=timezone.now()
)

# Notification statistics
notification_stats = Notification.objects.values('level').annotate(
    count=Count('id'),
    unread_count=Count('id', filter=Q(is_read=False))
)

# Recent activity
recent_notifications = Notification.objects.filter(
    created_at__gte=timezone.now() - timezone.timedelta(days=7)
).order_by('-created_at')

# User presence analytics
online_users = UserPresence.objects.filter(
    is_online=True
).select_related('user')
```

### Raw SQL Queries

#### Using Django's raw() method
```python
# Custom SQL query
results = User.objects.raw("""
    SELECT
        u.id,
        u.username,
        u.email,
        COUNT(n.id) as notification_count,
        MAX(n.created_at) as last_notification
    FROM
        auth_user u
    LEFT JOIN
        notifications_notification n ON u.id = n.user_id
    GROUP BY
        u.id, u.username, u.email
    ORDER BY
        notification_count DESC
""")
```

#### Using connection.cursor()
```python
from django.db import connection

def get_user_analytics():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                DATE_TRUNC('day', n.created_at) as date,
                COUNT(*) as notification_count,
                COUNT(CASE WHEN n.is_read = false THEN 1 END) as unread_count
            FROM
                notifications_notification n
            WHERE
                n.created_at >= %s
            GROUP BY
                DATE_TRUNC('day', n.created_at)
            ORDER BY
                date DESC
            LIMIT 30
        """, [timezone.now() - timezone.timedelta(days=30)])

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return results
```

## Database Optimization

### Indexing Strategy

#### Automatic Indexes
Django automatically creates indexes for:
- Primary keys
- Foreign keys
- Fields with `unique=True`
- Fields with `db_index=True`

#### Custom Indexes
```python
# Add to models.py
class Notification(models.Model):
    # ... existing fields ...

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['level', 'is_read']),
            models.Index(fields=['created_at']),
        ]

class UserSettings(models.Model):
    # ... existing fields ...

    class Meta:
        indexes = [
            models.Index(fields=['subscription_status']),
            models.Index(fields=['subscription_plan', 'subscription_status']),
            models.Index(fields=['subscription_end_date']),
        ]
```

#### Manual Index Creation
```sql
-- Create composite index for notifications
CREATE INDEX CONCURRENTLY idx_notifications_user_created
ON notifications_notification (user_id, created_at DESC);

-- Create index for subscription queries
CREATE INDEX CONCURRENTLY idx_usersettings_subscription
ON dashboard_usersettings (subscription_status, subscription_end_date);

-- Create partial index for unread notifications
CREATE INDEX CONCURRENTLY idx_notifications_unread
ON notifications_notification (user_id, created_at)
WHERE is_read = false;
```

### Query Optimization

#### Efficient Queries
```python
# Good: Use select_related for foreign keys
notifications = Notification.objects.select_related('user').all()

# Good: Use prefetch_related for many-to-many/reverse foreign keys
users = User.objects.prefetch_related('notifications').all()

# Good: Use only() to limit fields
users = User.objects.only('id', 'username', 'email').all()

# Good: Use defer() to exclude heavy fields
users = User.objects.defer('profile_data').all()
```

#### Avoiding N+1 Queries
```python
# Bad: N+1 query problem
for user in User.objects.all():
    notifications = user.notifications.all()  # Separate query for each user

# Good: Prefetch related data
users = User.objects.prefetch_related('notifications').all()
for user in users:
    notifications = user.notifications.all()  # No additional queries
```

### Connection Pooling

#### Using django-postgrespool
```python
# Add to requirements.txt
django-postgrespool2==1.3.0

# Update settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django_postgrespool',
        # ... other settings ...
        'OPTIONS': {
            'MAX_CONNS': 20,
            'REUSE_CONNS': 5,
        }
    }
}
```

## Performance Monitoring

### Database Statistics

#### Using psql
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('your_db_name'));

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### Django Debug Toolbar
```python
# Add to requirements.txt
django-debug-toolbar==4.4.6

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

# Add to MIDDLEWARE
MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Add to settings.py
INTERNAL_IPS = ['127.0.0.1']
```

## Backup and Recovery

### Automated Backups

#### Using pg_dump
```bash
# Full backup
pg_dump -h localhost -U your_db_user your_db_name > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
pg_dump -h localhost -U your_db_user your_db_name | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Custom format backup (faster, more flexible)
pg_dump -h localhost -U your_db_user -Fc your_db_name > backup_$(date +%Y%m%d_%H%M%S).dump
```

#### Using pg_dumpall
```bash
# Backup all databases
pg_dumpall -h localhost -U postgres > all_databases_backup.sql
```

### Restoration

#### Restoring from backup
```bash
# From SQL file
psql -h localhost -U your_db_user -d your_db_name < backup_file.sql

# From compressed backup
gunzip -c backup_file.sql.gz | psql -h localhost -U your_db_user -d your_db_name

# From custom format
pg_restore -h localhost -U your_db_user -d your_db_name backup_file.dump
```

### Backup Script Example

```bash
#!/bin/bash
# backup_postgres.sh

DB_NAME="your_db_name"
DB_USER="your_db_user"
DB_HOST="localhost"
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create compressed backup
pg_dump -h $DB_HOST -U $DB_USER -Fc $DB_NAME > $BACKUP_DIR/backup_$DATE.dump

# Remove backups older than 7 days
find $BACKUP_DIR -name "backup_*.dump" -mtime +7 -delete

echo "Backup completed: backup_$DATE.dump"
```

## Security Considerations

### Database Security

#### User Permissions
```sql
-- Create read-only user
CREATE USER readonly_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE your_db_name TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Create backup user
CREATE USER backup_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE your_db_name TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
```

#### Connection Security
```python
# Use SSL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'sslmode': 'require',  # or 'verify-full' for certificate verification
        },
    }
}
```

### SQL Injection Prevention

#### Django ORM Protection
```python
# Safe: Django ORM automatically parameterizes queries
users = User.objects.filter(username=username)

# Dangerous: Raw SQL with string formatting (avoid)
cursor.execute(f"SELECT * FROM auth_user WHERE username = '{username}'")

# Safe: Parameterized raw SQL
cursor.execute("SELECT * FROM auth_user WHERE username = %s", [username])
```

## Scaling Considerations

### Read Replicas

#### Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'primary_db',
        'HOST': 'primary-db-host',
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'replica_db',
        'HOST': 'replica-db-host',
    }
}

# Database router for read/write splitting
class ReplicationRouter:
    def db_for_read(self, model, **hints):
        return 'replica'

    def db_for_write(self, model, **hints):
        return 'default'
```

### Connection Limits

#### PostgreSQL Configuration
```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check max connections
SHOW max_connections;

-- Set max connections (requires restart)
ALTER SYSTEM SET max_connections = 200;
SELECT pg_reload_conf();
```

## Troubleshooting

### Common Issues

#### Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Test connection
psql -h localhost -U your_db_user -d your_db_name -c "SELECT 1;"
```

#### Performance Issues
```sql
-- Check active connections
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Check long-running queries
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Kill long-running query
SELECT pg_terminate_backend(pid);
```

#### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

-- Force migration (use with caution)
python manage.py migrate --fake

-- Reset migrations (development only)
python manage.py migrate app_name zero
python manage.py makemigrations app_name
python manage.py migrate app_name
```

## Monitoring Tools

### Django Applications

#### django-postgres-extras
```python
# Add to requirements.txt
django-postgres-extras==2.0.8

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'postgres_extras',
]

# Add to settings.py
POSTGRES_EXTRAS = {
    'ENABLE_ADMIN': True,
}
```

#### pgAdmin
Web-based PostgreSQL administration tool: https://www.pgadmin.org/

### Command Line Tools

#### psqlbar
```bash
# Progress bar for long-running queries
psql -h localhost -U your_db_user -d your_db_name -c "SELECT pg_stat_progress_vacuum;"
```

#### pgbench
```bash
# Database benchmarking
pgbench -i your_db_name
pgbench -c 10 -j 2 -t 1000 your_db_name
```

## Best Practices

### Development

1. **Use SQLite for development**, PostgreSQL for production
2. **Keep migrations under version control**
3. **Use Django fixtures for test data**
4. **Test queries with EXPLAIN ANALYZE**
5. **Monitor query performance regularly**

### Production

1. **Use connection pooling**
2. **Configure appropriate indexes**
3. **Implement regular backups**
4. **Monitor database performance**
5. **Use read replicas for scaling**
6. **Implement proper security measures**

### Performance

1. **Optimize frequent queries**
2. **Use database views for complex queries**
3. **Implement caching where appropriate**
4. **Monitor slow queries**
5. **Regular VACUUM and ANALYZE**

This comprehensive PostgreSQL integration guide provides all the necessary information for setting up, managing, and optimizing PostgreSQL with the Django project.