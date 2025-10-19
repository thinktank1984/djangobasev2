#!/bin/zsh
# Claude Code launcher script - can be executed directly

# Check if venv exists in current directory and activate it
if [[ -d "venv" ]]; then
    echo "Activating Python virtual environment from $(pwd)..."
    source venv/bin/activate
else
    echo "No virtual environment found in $(pwd), skipping activation..."
fi



echo "Starting Claude Code..."

# No arguments - start interactive mode
claude   --dangerously-skip-permissions 
