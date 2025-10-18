# Dockerfile for Emmett Runtime Application
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright system dependencies (for browser automation)
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 24
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Gemini CLI globally
RUN npm install -g @google/gemini-cli@latest

# Install Tailwind CSS standalone CLI
# Detect architecture and download appropriate binary
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 && \
        chmod +x tailwindcss-linux-x64 && \
        mv tailwindcss-linux-x64 /usr/local/bin/tailwind; \
    elif [ "$ARCH" = "aarch64" ]; then \
        curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-arm64 && \
        chmod +x tailwindcss-linux-arm64 && \
        mv tailwindcss-linux-arm64 /usr/local/bin/tailwind; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi

# Copy requirements file for Python dependencies
COPY setup/requirements.txt /tmp/requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Install Playwright browsers (Chromium for testing)
RUN playwright install chromium --with-deps

# The full repository will be mounted at runtime via volume
# No need to copy files - they'll be available via volume mount

# Expose port for the Emmett application
EXPOSE 8081

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV EMMETT_ENV=development

# Command will be specified in docker-compose.yaml
# Default command for standalone usage:
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8081", "runtime.app:app"]

