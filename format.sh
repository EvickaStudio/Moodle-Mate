#! /bin/bash

# Apply Ruff linter and auto-fix issues
ruff check . --fix

# Apply Ruff formatter
ruff format .

echo "Linting and formatting complete with Ruff!"
