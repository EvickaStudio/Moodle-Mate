#!/bin/sh
set -eu

# Export runtime and development dependencies together with lockfile hashes.
uv export --frozen --no-dev --extra dev --no-emit-project -o "${1:-requirements-dev.txt}" >/dev/null
