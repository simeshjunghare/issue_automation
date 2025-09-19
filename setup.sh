#!/bin/bash

# Exit on any error
set -e

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright
echo "Installing Playwright..."
python -m playwright install

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install --force chromium

# Install system dependencies (only on Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing system dependencies..."
    python -m playwright install-deps
fi

echo "Setup completed successfully!"

exit 0
