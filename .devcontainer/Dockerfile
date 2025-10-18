# Django Development Environment Dockerfile
# Optimized for DjangoBaseV2 project with all necessary dependencies

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/workspaces/djangobasev2/blogapp \
    DJANGO_SETTINGS_MODULE=core.settings \
    DEBUG=1

# Set work directory
WORKDIR /workspaces/djangobasev2

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    build-essential \
    curl \
    wget \
    git \
    # Database dependencies
    libpq-dev \
    libsqlite3-dev \
    libffi-dev \
    libssl-dev \
    # Image processing libraries
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    lcms2-dev \
    # Other utilities
    vim \
    nano \
    tree \
    htop \
    postgresql-client \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install Node.js for frontend tools (Tailwind CSS, etc.)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install Python build tools
RUN pip install --upgrade pip setuptools wheel pip-tools

# Create non-root user for development
RUN useradd -ms /bin/bash vscode && \
    echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Install Python dependencies
# Copy requirements first for better Docker layer caching
COPY blogapp/requirements.txt /tmp/requirements.txt

# Install Python requirements
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install additional development tools
RUN pip install --no-cache-dir \
    # Code quality tools
    black \
    isort \
    flake8 \
    mypy \
    pre-commit \
    # Testing tools
    pytest \
    pytest-django \
    pytest-cov \
    coverage \
    # Django extensions
    django-debug-toolbar \
    django-extensions \
    # Documentation
    sphinx \
    sphinx-rtd-theme

# Install global Node.js packages for development
RUN npm install -g \
    tailwindcss \
    postcss \
    autoprefixer \
    prettier \
    eslint

# Change ownership of the workspace
RUN chown -R vscode:vscode /workspaces/djangobasev2

# Switch to non-root user
USER vscode

# Set up Python paths
ENV PATH="/home/vscode/.local/bin:$PATH"

# Create cache directories
RUN mkdir -p /home/vscode/.cache/pip && \
    mkdir -p /tmp/django_static

# Create useful aliases
RUN echo 'alias manage="cd /workspaces/djangobasev2/blogapp && python manage.py"' >> /home/vscode/.bashrc && \
    echo 'alias runserver="cd /workspaces/djangobasev2/blogapp && python manage.py runserver 0.0.0.0:8000"' >> /home/vscode/.bashrc && \
    echo 'alias migrate="cd /workspaces/djangobasev2/blogapp && python manage.py migrate"' >> /home/vscode/.bashrc && \
    echo 'alias collectstatic="cd /workspaces/djangobasev2/blogapp && python manage.py collectstatic --noinput"' >> /home/vscode/.bashrc && \
    echo 'alias shell="cd /workspaces/djangobasev2/blogapp && python manage.py shell"' >> /home/vscode/.bashrc && \
    echo 'alias test="cd /workspaces/djangobasev2/blogapp && python manage.py test"' >> /home/vscode/.bashrc && \
    echo 'alias dj="cd /workspaces/djangobasev2/blogapp"' >> /home/vscode/.bashrc

# Display welcome message
RUN echo 'echo "🐍 Django Development Environment Ready!"' >> /home/vscode/.bashrc && \
    echo 'echo "📝 Useful commands:"' >> /home/vscode/.bashrc && \
    echo 'echo "   manage [command]   - Run Django management commands"' >> /home/vscode/.bashrc && \
    echo 'echo "   runserver          - Start Django development server on port 8000"' >> /home/vscode/.bashrc && \
    echo 'echo "   migrate            - Run database migrations"' >> /home/vscode/.bashrc && \
    echo 'echo "   collectstatic      - Collect static files"' >> /home/vscode/.bashrc && \
    echo 'echo "   shell              - Open Django shell"' >> /home/vscode/.bashrc && \
    echo 'echo "   test               - Run Django tests"' >> /home/vscode/.bashrc && \
    echo 'echo "   dj                 - Change to Django project directory"' >> /home/vscode/.bashrc

# Expose ports
EXPOSE 8000 3000

# Set the working directory
WORKDIR /workspaces/djangobasev2/blogapp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1

# Default command (can be overridden)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]