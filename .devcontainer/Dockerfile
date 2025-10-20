# ------------------------------------------------------------
# DjangoBaseV2 Codespace image
# Ubuntu 24.04 + Python 3.12 + Node 24 + Claude Code + Gemini + OpenSpec
# ------------------------------------------------------------
FROM ubuntu:24.04

# ------------------------------------------------------------
# 🌍 Environment variables
# ------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PNPM_HOME=/usr/local/pnpm \
    PATH=$PNPM_HOME:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin

# Claude Code / Z.ai environment
ENV ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="b0d8bc10b7274fde891719c0f5fae80a.227yTm8wFgBMcyJW" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"

WORKDIR /app

# ------------------------------------------------------------
# 🧩 System setup
# ------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv python3-dev \
        curl git build-essential libpq-dev postgresql-client \
        ca-certificates gnupg lsb-release && \
    # --- Install Docker CLI (for Codespaces) ---
    apt-get install -y docker-cli && \
    # --- Install Node.js 24.x ---
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm && \
    rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 🐍 Install uv
# ------------------------------------------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /etc/bash.bashrc

# ------------------------------------------------------------
# 🤖 Install global CLIs
# ------------------------------------------------------------
RUN pnpm add -g @anthropic-ai/claude-code @google/gemini-cli @fission-ai/openspec

# ------------------------------------------------------------
# 📦 Install Python dependencies
# ------------------------------------------------------------
COPY setup/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# 🧱 Copy Django project and collect static files
# ------------------------------------------------------------
COPY . .
RUN mkdir -p /app/staticfiles /app/media && \
    python3 manage.py collectstatic --noinput || true

# ------------------------------------------------------------
# 👤 Create non-root user
# ------------------------------------------------------------
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# ------------------------------------------------------------
# ✅ Verify versions
# ------------------------------------------------------------
RUN echo "🐍 Python:" $(python3 --version) && \
    echo "🟢 Node:" $(node -v) && \
    echo "📦 pnpm:" $(pnpm -v) && \
    echo "🐋 Docker CLI:" $(docker --version || echo 'Installed') && \
    echo "🤖 Claude Code CLI:" $(claude --version || echo 'Available after shell login') && \
    echo "✨ Gemini CLI:" $(gemini --version || echo 'Available after shell login')

# ------------------------------------------------------------
# 💓 Health check & startup
# ------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

# Default entrypoint
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
