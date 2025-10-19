#!/usr/bin/env bash
set -e

echo "🚀 Setting up Codespace environment..."

# Install uv (modern Python env manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# Install pnpm + Claude Code CLI
curl -fsSL https://get.pnpm.io/install.sh | bash -
export PATH="$HOME/.local/share/pnpm:$PATH"
pnpm install -g @anthropic-ai/claude-code @google/gemini-cli

echo "✅ Claude Code ready! Run 'claude --help'"
