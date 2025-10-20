# ------------------------------------------------------------
# DjangoBaseV2 Codespace App Image
# Ubuntu 24.04 + Python 3.12 + Node 24 + uv + pnpm + CLIs
# ------------------------------------------------------------
FROM ubuntu:24.04

# ------------------------------------------------------------
# 🌍 Environment Variables
# ------------------------------------------------------------
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PNPM_HOME=/usr/local/pnpm \
    PATH=$PNPM_HOME:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="b0d8bc10b7274fde891719c0f5fae80a.227yTm8wFgBMcyJW" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"

WORKDIR /app

# ------------------------------------------------------------
# 🧩 System Setup
# ------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates curl git build-essential lsb-release gnupg \
        python3 python3-pip python3-venv python3-dev libpq-dev postgresql-client && \
    \
    # --- Install Node.js 24 + pnpm ---
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && npm install -g pnpm && \
    \
    # --- Clean up ---
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 🐍 Install uv
# ------------------------------------------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /etc/bash.bashrc

# ------------------------------------------------------------
# 🤖 Install Global CLIs
# ------------------------------------------------------------
RUN pnpm add -g @anthropic-ai/claude-code @google/gemini-cli @fission-ai/openspec

# ------------------------------------------------------------
# 📦 Python Dependencies
# ------------------------------------------------------------
COPY setup/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# 🧱 Copy Project & Collect Static Files
# ------------------------------------------------------------
COPY . .
RUN mkdir -p /app/staticfiles /app/media && \
    python3 manage.py collectstatic --noinput || true

# ------------------------------------------------------------
# 👤 Non-root User
# ------------------------------------------------------------
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# ------------------------------------------------------------
# ✅ Verify Versions
# ------------------------------------------------------------
RUN echo "🐍 Python:" $(python3 --version) && \
    echo "🟢 Node:" $(node -v) && \
    echo "📦 pnpm:" $(pnpm -v) && \
    echo "🐘 PostgreSQL Client:" $(psql --version) && \
    echo "🤖 Claude Code CLI:" $(claude --version || echo 'Available after login') && \
    echo "✨ Gemini CLI:" $(gemini --version || echo 'Available after login')

# ------------------------------------------------------------
# 💓 Health Check & Startup
# ------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

# ------------------------------------------------------------
# 🚀 Entrypoint
# ------------------------------------------------------------
CMD gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
