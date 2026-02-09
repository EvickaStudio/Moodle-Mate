SHELL := /bin/sh
.DEFAULT_GOAL := help

UV ?= uv
APP ?= moodlemate

.PHONY: help install install-dev bootstrap run run-module test test-cov test-ci format format-check lint lint-check check ci-lint ci-test ci-local clean lock lock-upgrade export-requirements export-requirements-runtime export-requirements-dev sync sync-dev refresh docker-build docker-up docker-down docker-logs docker-restart test-notification

help: ## Show available targets
	@echo "Available targets:"
	@grep -E '^[a-zA-Z0-9_.-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install runtime dependencies (uv sync)
	$(UV) sync

install-dev: ## Install runtime + development dependencies
	$(UV) sync --extra dev

bootstrap: install-dev ## Alias for install-dev

run: ## Run Moodle Mate via project entrypoint
	$(UV) run $(APP)

run-module: ## Run Moodle Mate as Python module
	$(UV) run python -m moodlemate

test: ## Run pytest test suite
	$(UV) run pytest

test-cov: ## Run tests with coverage report
	$(UV) run pytest --cov=src/moodlemate --cov-report=term-missing

test-ci: ## Run CI-aligned tests (quiet output)
	$(UV) run pytest -q

format: ## Format code with Ruff
	$(UV) run ruff format .

format-check: ## Check formatting without modifying files
	$(UV) run ruff format --check .

lint: ## Lint and auto-fix with Ruff
	$(UV) run ruff check --fix .

lint-check: ## Lint without auto-fixes
	$(UV) run ruff check --output-format=concise .

check: format lint ## Run formatter + linter

ci-lint: lint-check format-check ## CI-aligned lint checks (non-mutating)

ci-test: test-ci ## CI-aligned test checks

ci-local: ci-lint ci-test ## Run the same lint+test checks used by CI workflows

clean: ## Remove Python cache artifacts
	./scripts/clean.sh

lock: ## Refresh uv.lock
	$(UV) lock

lock-upgrade: ## Upgrade dependencies to latest compatible versions and refresh uv.lock
	$(UV) lock --upgrade

export-requirements: export-requirements-runtime ## Backward-compatible alias for runtime requirements export

export-requirements-runtime: ## Export runtime requirements.txt from uv lock
	$(UV) export --package moodle-mate --no-dev --no-emit-project -o requirements.txt

export-requirements-dev: ## Export additive requirements-dev.txt from pyproject dev extras
	./scripts/export_requirements_dev.sh requirements-dev.txt

sync: lock export-requirements-runtime export-requirements-dev ## Refresh lockfile and both requirements files

sync-dev: lock-upgrade install-dev export-requirements-runtime export-requirements-dev ## Upgrade lockfile, sync runtime+dev deps, and refresh both requirements files

refresh: sync check ## Refresh lockfile/requirements and run format+lint

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start Docker stack in background
	HOST_UID=$$(id -u) HOST_GID=$$(id -g) docker compose up -d --force-recreate --remove-orphans

docker-down: ## Stop Docker stack
	docker compose down

docker-logs: ## Follow Docker logs
	docker compose logs -f

docker-restart: docker-down docker-up ## Restart Docker stack

test-notification: ## Send a test notification using current .env config
	$(UV) run $(APP) --test-notification
