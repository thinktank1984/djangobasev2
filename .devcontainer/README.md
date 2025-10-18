# DevPod Development Environment for DjangoBaseV2

This directory contains the DevPod configuration for the DjangoBaseV2 project, providing a complete, isolated development environment.

## Quick Start

### Prerequisites

1. **Install DevPod CLI**:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/loft-sh/devpod/main/install.sh | bash
   ```

2. **Verify Installation**:
   ```bash
   devpod version
   ```

### Starting Development Environment

```bash
# From the project root directory
devpod up

# Or open directly in VS Code
devpod up --ide vscode
```

### Connecting to Environment

```bash
# SSH into the development environment
devpod ssh

# Or use VS Code (recommended)
devpod up --ide vscode
```

### Running Django Commands

Once inside the DevPod environment:

```bash
# Change to Django project directory
cd blogapp

# Start development server
python manage.py runserver 0.0.0.0:8000

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Open Django shell
python manage.py shell
```

## Available Services

### Database Services

- **PostgreSQL**: `localhost:5432`
  - Database: `djangobasev2_dev`
  - User: `postgres`
  - Password: `postgres`

- **Redis**: `localhost:6379`
  - Used for caching and Celery tasks

- **MinIO**: `localhost:9000` (API), `localhost:9001` (Console)
  - S3-compatible storage
  - Access Key: `minioadmin`
  - Secret: `minioadmin123`

- **Mailhog**: `localhost:8025` (Web UI), `localhost:1025` (SMTP)
  - Email testing in development

- **Elasticsearch**: `localhost:9200`
  - Search functionality (optional)

### Development Tools

- **Django Debug Toolbar**: Enabled in development
- **Django Extensions**: Additional management commands
- **Tailwind CSS**: For frontend styling
- **VS Code Extensions**: Pre-installed for Django development

## Environment Configuration

### Using Environment Files

The DevPod environment includes several environment files:

1. **`.env.devpod`**: Default DevPod configuration
2. **`.env.development`**: General development configuration
3. **`.env.example`**: Template with all available options

### Custom Environment Variables

Create `.devcontainer/.env.local` for project-specific overrides:

```bash
# Copy the development environment file
cp .devcontainer/.env.development .devcontainer/.env.local

# Edit with your specific settings
nano .devcontainer/.env.local
```

## Development Workflow

### 1. Environment Setup

```bash
# Start DevPod environment
devpod up

# Connect to environment
devpod ssh
```

### 2. Database Setup

```bash
# Run migrations
cd blogapp
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Load fixtures (if available)
python manage.py loaddata fixtures/initial_data.json
```

### 3. Frontend Development

```bash
# Install Node.js dependencies (if package.json exists)
npm install

# Compile Tailwind CSS
npx tailwindcss -i ./theme/static_src/input.css -o ./theme/static/dist/output.css --watch
```

### 4. Running Services

```bash
# Start Django development server
python manage.py runserver 0.0.0.0:8000

# Start Celery worker (if using background tasks)
celery -A core worker -l info

# Start Celery beat (if using scheduled tasks)
celery -A core beat -l info
```

### 5. Testing

```bash
# Run Django tests
python manage.py test

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## VS Code Integration

### Extensions Automatically Installed

- **Python**: Language support and debugging
- **Django**: Django-specific features
- **Tailwind CSS**: CSS class completion
- **Black Formatter**: Python code formatting
- **GitLens**: Git integration
- **Prettier**: Code formatting

### Debugging Configuration

The environment includes pre-configured Django debugging. Set breakpoints in VS Code and use the debugger:

1. Open VS Code in DevPod: `devpod up --ide vscode`
2. Set breakpoints in your Python code
3. Go to "Run and Debug" panel
4. Select "Django" configuration
5. Press F5 to start debugging

## Troubleshooting

### Common Issues

1. **Port Conflicts**:
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   # Or use a different port
   python manage.py runserver 0.0.0.0:8001
   ```

2. **Database Connection Issues**:
   ```bash
   # Check PostgreSQL container status
   docker ps | grep postgres
   # Restart services if needed
   docker-compose -f .devcontainer/docker-compose.yml restart
   ```

3. **Permission Issues**:
   ```bash
   # Fix file permissions
   sudo chown -R vscode:vscode /workspaces/djangobasev2
   ```

4. **Outdated Dependencies**:
   ```bash
   # Update Python packages
   pip install --upgrade -r blogapp/requirements.txt
   # Update Node.js packages
   npm update
   ```

### Getting Help

1. **Check DevPod logs**:
   ```bash
   devpod logs <environment-name>
   ```

2. **Restart environment**:
   ```bash
   devpod stop
   devpod up --recreate
   ```

3. **Debug mode**:
   ```bash
   devpod up --debug
   ```

## Advanced Usage

### Custom Configuration

You can customize the DevPod environment by modifying:

- **`devpod.yaml`**: Main DevPod configuration
- **`Dockerfile`**: Container image definition
- **`devcontainer.json`**: VS Code specific settings
- **`docker-compose.yml`**: Additional services

### Performance Optimization

1. **Enable caching** in `devpod.yaml`
2. **Use resource limits** to prevent system overload
3. **Optimize Docker layering** in Dockerfile

### Team Collaboration

1. **Commit `.devcontainer/`** to version control
2. **Share environment file templates** (`.env.example`)
3. **Document any project-specific setup** in this README

## File Structure

```
.devcontainer/
├── README.md                 # This file
├── devpod.yaml              # Main DevPod configuration
├── devcontainer.json        # VS Code configuration
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Additional services
├── init.sql                 # PostgreSQL initialization
├── post-create.sh           # Container setup script
├── .env.example             # Environment template
├── .env.development         # Development environment
├── .env.devpod             # DevPod-specific environment
└── .env.local              # Local overrides (don't commit)
```

## Environment Variables Reference

Key environment variables used in this setup:

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `core.settings` | Django settings module |
| `DEBUG` | `True` | Django debug mode |
| `DATABASE_URL` | PostgreSQL config | Database connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection |
| `EMAIL_HOST` | `localhost` | Email server (Mailhog) |
| `SECRET_KEY` | Generated | Django secret key |

For a complete list, see `.devcontainer/.env.example`.

## Support

- **DevPod Documentation**: https://devpod.sh/docs
- **Django Documentation**: https://docs.djangoproject.com/
- **Project Issues**: Create an issue in the project repository