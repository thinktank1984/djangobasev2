# ------------------------------------------------------------
# DjangoBaseV2 Alpine Image
# Alpine 3.20 + Python 3.12 + Node 24 + uv + pnpm + CLIs
# ------------------------------------------------------------
FROM alpine:3.20

# ------------------------------------------------------------
# 🌍 Environment
# ------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PNPM_HOME=/usr/local/pnpm \
    PATH=$PNPM_HOME:/usr/local/bin:$PATH \
    DEBIAN_FRONTEND=noninteractive \
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="b0d8bc10b7274fde891719c0f5fae80a.227yTm8wFgBMcyJW" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6" \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"

WORKDIR /app

# ------------------------------------------------------------
# 🧩 System Setup
# ------------------------------------------------------------
RUN apk add --no-cache \
    bash curl git build-base libpq-dev postgresql-client \
    python3 py3-pip py3-virtualenv py3-wheel py3-setuptools \
    nodejs npm

# ------------------------------------------------------------
# 🧰 Tools
# ------------------------------------------------------------
RUN npm install -g pnpm && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    pnpm add -g @anthropic-ai/claude-code @google/gemini-cli @fission-ai/openspec

# ------------------------------------------------------------
# 📦 Dependencies
# ------------------------------------------------------------
COPY setup/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# 🧱 Project Copy
# ------------------------------------------------------------
COPY . .
RUN mkdir -p /app/staticfiles /app/media && chmod -R 777 /app

# ------------------------------------------------------------
# 👤 User
# ------------------------------------------------------------
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# ------------------------------------------------------------
# ✅ Version Check
# ------------------------------------------------------------
RUN echo "🐍 Python:" $(python3 --version) && \
    echo "🟢 Node:" $(node -v) && \
    echo "📦 pnpm:" $(pnpm -v) && \
    echo "🐘 psql:" $(psql --version)

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
