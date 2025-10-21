# ============================================================
# 🐋 DjangoBaseV2 Dev Container Image
# Debian Bullseye + Python 3.12 + Node 24 + PostgreSQL client + uv
# ============================================================

# ------------------------------------------------------------
# 🐋 Base and PostgreSQL Setup
# ------------------------------------------------------------
FROM mcr.microsoft.com/devcontainers/python:3.12-bullseye

ENV PYTHONUNBUFFERED=1

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive

# Install PostgreSQL client tools (v16)
RUN apt-get -y install --no-install-recommends postgresql-common \
    && /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y && \
    apt-get -y install --no-install-recommends postgresql-client-16 \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 🌍 Environment
# ------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PNPM_HOME=/usr/local/pnpm \
    PATH=$PNPM_HOME:/usr/local/bin:$PATH \
    DEBIAN_FRONTEND=noninteractive \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_LINK_MODE=copy \
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="b0d8bc10b7274fde891719c0f5fae80a.227yTm8wFgBMcyJW" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"

WORKDIR /app

# ------------------------------------------------------------
# 🧩 System Setup
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl git build-essential libpq-dev python3-venv python3-wheel python3-setuptools \
    ca-certificates gnupg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# 🟢 Install Node.js 24 + npm
# ------------------------------------------------------------
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    node -v && npm -v

# ------------------------------------------------------------
# ⚡ Install uv (Python package manager)
# ------------------------------------------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | bash && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    uv --version

# ------------------------------------------------------------
# 🧰 Tools (pnpm + AI CLIs)
# ------------------------------------------------------------
ENV PNPM_HOME=/usr/local/pnpm
ENV PATH=$PNPM_HOME:/usr/local/bin:$PATH

RUN mkdir -p "$PNPM_HOME" && \
    npm install -g pnpm && \
    pnpm add -g @anthropic-ai/claude-code @google/gemini-cli @fission-ai/openspec

# ------------------------------------------------------------
# 📦 Python Dependencies (using uv)
# ------------------------------------------------------------
COPY setup/requirements.txt ./requirements.txt
RUN uv pip install --system -r requirements.txt

# ------------------------------------------------------------
# 📁 Project Files
# ------------------------------------------------------------
COPY . .
RUN mkdir -p /app/staticfiles /app/media && chmod -R 777 /app

# ------------------------------------------------------------
# 👤 Non-root User
# ------------------------------------------------------------
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# ------------------------------------------------------------
# 🧾 Version Check
# ------------------------------------------------------------
RUN echo "🐍 Python: $(python3 --version)" && \
    echo "🟢 Node: $(node -v)" && \
    echo "📦 pnpm: $(pnpm -v)" && \
    echo "💡 uv: $(uv --version)" && \
    echo "🐘 psql: $(psql --version)"

# ------------------------------------------------------------
# 💓 Health Check
# ------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

# ------------------------------------------------------------
# 🚀 Entrypoint
# ------------------------------------------------------------
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
