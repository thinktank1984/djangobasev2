# DevPod - Open Source Dev-Environments-As-Code

**Official Website**: https://devpod.sh/

## Overview

DevPod is an open-source development environment as code tool that allows you to create reproducible development environments quickly and easily. It's perfect for team collaboration and ensuring consistent development setups across different machines.

## Why Use DevPod?

- **Reproducible Environments**: Every developer gets the exact same development setup
- **Fast Setup**: Spin up new environments in minutes, not hours
- **Provider Agnostic**: Works with Docker, Kubernetes, cloud providers, and more
- **IDE Integration**: Works with VS Code, JetBrains IDEs, and more
- **Team Collaboration**: Share development environments with your team
- **Isolation**: Keep your host machine clean with containerized environments

## Installation

### Install DevPod CLI

```bash
# Install using the installation script
curl -fsSL https://raw.githubusercontent.com/loft-sh/devpod/main/install.sh | bash

# Or install via Homebrew (macOS)
brew install loft-sh/tap/devpod

# Or install via Scoop (Windows)
scoop install loft-sh/devpod
```

### Verify Installation

```bash
devpod version
```

## Getting Started with DevPod

### 1. Create a DevPod Configuration

Create a `.devcontainer/devpod.yaml` file in your project root:

```yaml
version: v1beta8
name: djangobasev2-dev

# IDE configuration
ide:
  name: vscode
  # Automatically open VS Code when connecting
  open: true

# Development container configuration
dev:
  # Base image to use
  image: python:3.11-slim

  # Environment variables
  environment:
    - DJANGO_SETTINGS_MODULE=myproject.settings.development
    - PYTHONPATH=/workspaces/djangobasev2
    - DEBUG=1

  # Commands to run when starting the development environment
  init:
    - pip install --upgrade pip
    - pip install -r requirements.txt
    - python manage.py migrate
    - python manage.py collectstatic --noinput

  # Ports to forward
  ports:
    - port: 8000
      description: Django development server
    - port: 5432
      description: PostgreSQL database (if using local DB)

  # Volume mounts
  mount:
    - .:/workspaces/djangobasev2

  # Shell to use
  shell: /bin/bash

  # Commands to run continuously
  # (Useful for starting services automatically)
  # Note: These run in the background
  command:
    - python manage.py runserver 0.0.0.0:8000
```

### 2. Alternative: Use .devcontainer.json (VS Code compatible)

Create a `.devcontainer/devcontainer.json` file:

```json
{
  "name": "DjangoBaseV2 Development",
  "dockerFile": "Dockerfile",
  "context": "..",
  "settings": {
    "python.defaultInterpreterPath": "/usr/local/bin/python",
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
  },
  "extensions": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "batisteo.vscode-django",
    "ms-python.black-formatter"
  ],
  "forwardPorts": [8000],
  "postCreateCommand": "pip install --upgrade pip && pip install -r requirements.txt && python manage.py migrate",
  "remoteUser": "vscode"
}
```

And a corresponding `.devcontainer/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        git \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Create app user
RUN useradd -ms /bin/bash vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /workspaces
USER vscode
```

### 3. Start Development Environment

```bash
# Start the development environment
devpod up

# Connect to the environment
devpod ssh

# Or open in VS Code directly
devpod up --ide vscode

# Stop the environment
devpod stop

# Delete the environment
devpod delete
```

## Project-Specific Configuration for DjangoBaseV2

### Environment Variables Setup

Create a `.env` file for your development environment:

```bash
# Database settings
DATABASE_URL=postgresql://postgres:password@localhost:5432/djangobasev2_dev

# Django settings
DJANGO_SETTINGS_MODULE=myproject.settings.development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Email settings (for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Database Setup

Option 1: Use PostgreSQL in Docker

```yaml
# Add to your devpod.yaml or create docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: djangobasev2_dev
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

Option 2: Use SQLite (simpler for development)

```bash
# In your Django settings, use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

## Useful DevPod Commands

### Environment Management

```bash
# List all development environments
devpod list

# Show details of a specific environment
devpod status <environment-name>

# Stop an environment
devpod stop <environment-name>

# Start a stopped environment
devpod start <environment-name>

# Delete an environment
devpod delete <environment-name>

# Update an environment
devpod up --recreate
```

### Development Workflow

```bash
# Enter the development environment
devpod ssh

# Once inside, run Django commands
python manage.py runserver 0.0.0.0:8000
python manage.py migrate
python manage.py createsuperuser
python manage.py test
```

### Working with Files

```bash
# Copy files from host to dev environment
devpod cp /path/to/local/file <environment-name>:/path/in/container

# Copy files from dev environment to host
devpod cp <environment-name>:/path/in/container /path/to/local
```

## IDE Integration

### VS Code Integration

1. Install the DevPod VS Code extension
2. Use `devpod up --ide vscode` to open directly in VS Code
3. All your VS Code settings and extensions will be available

### JetBrains Integration

```bash
# For PyCharm
devpod up --ide pycharm

# For IntelliJ IDEA
devpod up --ide intellij

# For WebStorm
devpod up --ide webstorm
```

## Providers

DevPod supports multiple providers:

### Docker (Default)

```bash
# Use Docker (default)
devpod up --provider docker
```

### Kubernetes

```bash
# Use Kubernetes cluster
devpod up --provider kubernetes
```

### Cloud Providers

```bash
# AWS
devpod up --provider aws

# Google Cloud
devpod up --provider gcp

# Azure
devpod up --provider azure
```

## Best Practices

### 1. Keep Secrets Out of Configuration

- Use environment variables for sensitive data
- Never commit passwords, API keys, or secrets to version control
- Use `.env` files and add them to `.gitignore`

### 2. Optimize Performance

```yaml
# Add caching for pip packages
cache:
  - path: ~/.cache/pip
  - path: node_modules
```

### 3. Health Checks

```yaml
# Add health checks for services
health:
  command: python manage.py check
  interval: 30s
  timeout: 10s
  retries: 3
```

### 4. Resource Limits

```yaml
# Set resource limits
resources:
  limits:
    cpu: "2"
    memory: "4Gi"
  requests:
    cpu: "1"
    memory: "2Gi"
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Make sure ports 8000 and 5432 are not in use
2. **Permission Issues**: Ensure proper user permissions in the container
3. **Network Issues**: Check Docker daemon is running
4. **Build Failures**: Clear cache with `devpod up --recreate`

### Debug Mode

```bash
# Run with verbose output
devpod up --debug

# Check logs
devpod logs <environment-name>
```

### Reset Everything

```bash
# Stop and remove all environments
devpod stop --all
devpod delete --all
```

## Team Collaboration

### Sharing Configurations

Commit your `.devcontainer/` directory to version control to share the development environment configuration with your team.

### Consistent Environments

Every team member running `devpod up` will get the exact same development environment, eliminating "it works on my machine" issues.

## Resources

- [Official Documentation](https://devpod.sh/docs)
- [GitHub Repository](https://github.com/loft-sh/devpod)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=loft-sh.devpod)
- [Community](https://github.com/loft-sh/devpod/discussions)

## Quick Start for This Project

```bash
# 1. Clone the repository
git clone <repository-url>
cd djangobasev2

# 2. Create .devcontainer directory
mkdir .devcontainer

# 3. Add the configuration files (see examples above)

# 4. Start development environment
devpod up

# 5. Connect and start developing
devpod ssh
python manage.py runserver 0.0.0.0:8000
```

This will give you a fully functional Django development environment with all dependencies installed and the development server running!

