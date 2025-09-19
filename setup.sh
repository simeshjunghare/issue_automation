#!/bin/bash

# Install Playwright browsers
python -m playwright install --force
python -m playwright install-deps

# Make sure the script is executable
chmod +x setup.sh
