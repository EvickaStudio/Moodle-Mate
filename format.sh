#! /bin/bash

set -euo pipefail

# uv lock
uv lock

# Export requirements.txt for legacy tooling
uv export --no-emit-project -o requirements.txt

# Local formatting and linting using uv + Ruff
# Format first, then lint with auto-fixes to keep a clean working tree
uv run ruff format .
uv run ruff check --fix .
