#!/bin/bash

# Service23 startup script
# Data Analyst Agent API

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting Service23 - Data Analyst Agent API..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating..."
    uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "Warning: requirements.txt not found"
    fi
fi

# Load environment variables
if [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
    echo "Loaded environment from ../.env"
elif [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Loaded environment from .env"
fi

# Set default port if not set
export PORT=${PORT:-8023}
export HOST=${HOST:-0.0.0.0}

echo "Service23 will run on $HOST:$PORT"

# Run the FastAPI server
python api_server.py
