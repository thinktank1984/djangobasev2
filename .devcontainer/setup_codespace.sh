#!/usr/bin/env bash
set -e

echo "🚀 Setting up Codespace environment..."

# --- 1️⃣ Install uv -----------------------------------------------------------
if ! command -v uv >/dev/null 2>&1; then
  echo "📦 Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.cargo/bin:$PATH"
else
  echo "✅ uv already installed"
fi

# --- 2️⃣ Install pnpm ---------------------------------------------------------
if ! command -v pnpm >/dev/null 2>&1; then
  echo "📦 Installing pnpm..."
  curl -fsSL https://get.pnpm.io/install.sh | bash -
else
  echo "✅ pnpm already installed"
fi

# --- 3️⃣ Fix PATH for pnpm binaries ------------------------------------------
export PNPM_HOME="$HOME/.local/share/pnpm"
export PATH="$PNPM_HOME:$PATH"

# Persist paths in bashrc
grep -qxF 'export PNPM_HOME="$HOME/.local/share/pnpm"' ~/.bashrc || \
  echo 'export PNPM_HOME="$HOME/.local/share/pnpm"' >> ~/.bashrc
grep -qxF 'export PATH="$PNPM_HOME:$PATH"' ~/.bashrc || \
  echo 'export PATH="$PNPM_HOME:$PATH"' >> ~/.bashrc
grep -qxF 'export PATH="$HOME/.cargo/bin:$PATH"' ~/.bashrc || \
  echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc

# --- 4️⃣ Install global CLIs --------------------------------------------------
echo "📦 Installing Claude Code + Gemini CLI..."
pnpm add -g @anthropic-ai/claude-code @google/gemini-cli

echo "✅ CLI installation complete."

# --- 5️⃣ Add Z.ai GLM 4.6 environment config ----------------------------------
if ! grep -q "ANTHROPIC_BASE_URL" ~/.bashrc 2>/dev/null; then
  echo "🔑 Adding Z.ai GLM 4.6 configuration..."
  cat >> ~/.bashrc <<'EOF'

# Claude Code + GLM 4.6 integration (Z.ai)
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="b0d8bc10b7274fde891719c0f5fae80a.227yTm8wFgBMcyJW"
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
EOF
else
  echo "✅ Z.ai environment already configured"
fi

# --- 6️⃣ Verify installation --------------------------------------------------
echo "🎯 Verifying tools..."
if command -v claude >/dev/null 2>&1; then
  claude --version
else
  echo "⚠️  'claude' not in PATH yet — open a new terminal or run: source ~/.bashrc"
fi
# --- 6️⃣ Create uv virtual environment (venv, Python 3.12) --------------------
if [ ! -d "venv" ]; then
  echo "🐍 Creating uv virtual environment: ./venv (Python 3.12)"
  uv venv venv --python=python3.12

else
  echo "✅ uv virtual environment already exists"
fi
python3 --version || echo "⚠️  Python not found"


