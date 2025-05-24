@echo off

echo Running Ruff linter and auto-fix...
ruff check . --fix

echo Running Ruff formatter...
ruff format .

echo Linting and formatting complete with Ruff!
pause
