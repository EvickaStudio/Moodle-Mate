#! /bin/bash

set -euo pipefail

#uv lock
uv lock

# Compile requirements.txt
uv pip compile pyproject.toml -o requirements.txt  

# Local formatting and linting using uv + Ruff
# Format first, then lint with auto-fixes to keep a clean working tree
uvx ruff format .
uvx ruff check --fix .