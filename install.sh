#!/usr/bin/env bash
set -e

SCRIPT_DIR="."
APP_DIR="."

# Create virtualenv if it doesn't exist
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

# Activate virtualenv
source "$SCRIPT_DIR/.venv/bin/activate"

# Install dependencies
echo "Installing dependencies..."
pip install -r "$APP_DIR/requirements.txt"

# Start the app
echo "Starting the app..."
cd "$APP_DIR"
python app.py
