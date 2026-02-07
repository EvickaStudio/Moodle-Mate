#!/bin/sh
set -eu

# Remove Python cache directories and compiled artifacts.
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.pyd" \) -exec rm -f {} +
