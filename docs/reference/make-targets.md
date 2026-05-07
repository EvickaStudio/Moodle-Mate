---
icon: material/hammer
description: All Moodle Mate Makefile targets and their purpose.
---

# Make Targets Reference

Moodle Mate's `Makefile` centralises all common development, lint, test, and deployment tasks.

## Discovery

List every available target and its description:

```bash
make help
```

## Core development

| Target | Command(s) run | Purpose |
|--------|---------------|---------|
| `make install` | `uv sync` | Install runtime dependencies only |
| `make install-dev` | `uv sync --extra dev` | Install runtime + dev dependencies |
| `make bootstrap` | same as `install-dev` | Alias for `install-dev` |
| `make run` | `uv run moodlemate` | Run the app via project script |
| `make run-module` | `uv run python -m moodlemate` | Run the app as a Python module |
| `make test-notification` | `uv run moodlemate --test-notification` | Send a test notification with current `.env` |

## Quality checks

| Target | Mutates files? | Purpose |
|--------|---------------|---------|
| `make format` | ✅ yes | `ruff format .` — rewrites files in place |
| `make format-check` | ❌ no | `ruff format --check .` — used in CI |
| `make lint` | ✅ yes | `ruff check --fix .` — applies safe auto-fixes |
| `make lint-check` | ❌ no | `ruff check --output-format=concise .` — used in CI |
| `make check` | ✅ yes | `format` + `lint` |
| `make ci-lint` | ❌ no | `lint-check` + `format-check` — CI-aligned |
| `make typecheck` | ❌ no | `pyright` — static type analysis |
| `make typecheck-warnings` | ❌ no | `pyright --level warning` |

## Testing

| Target | Purpose |
|--------|---------|
| `make test` | Run full pytest suite |
| `make test-cov` | Run pytest with coverage report |
| `make test-ci` | Run pytest with quiet output (CI format) |
| `make ci-test` | Alias for `test-ci` |
| `make ci-local` | `ci-lint` + `ci-test` — full CI suite locally |

## Dependency & lockfile management

| Target | Purpose |
|--------|---------|
| `make lock` | Refresh `uv.lock` |
| `make lock-upgrade` | Upgrade deps to latest compatible versions and refresh lock |
| `make export-requirements` | Alias for `export-requirements-runtime` |
| `make export-requirements-runtime` | Export `requirements.txt` from lockfile |
| `make export-requirements-dev` | Export `requirements-dev.txt` from dev extras |
| `make sync` | `lock` + both exports |
| `make sync-dev` | `lock-upgrade` + `install-dev` + both exports |
| `make refresh` | `sync` + `check` |

## Utility

| Target | Purpose |
|--------|---------|
| `make clean` | Remove Python cache artifacts (`__pycache__`, `.pyc`, etc.) |

## Docker

| Target | Purpose |
|--------|---------|
| `make docker-build` | Build Docker image |
| `make docker-up` | Start Docker stack in background |
| `make docker-down` | Stop Docker stack |
| `make docker-logs` | Follow Docker logs |
| `make docker-restart` | Stop then start Docker stack |

## Recommended usage patterns

=== "Daily development"

    ```bash
    make run      # run the app
    make test     # run tests
    make check    # format + lint (mutating)
    ```

=== "Before committing"

    ```bash
    make ci-local  # non-mutating lint + tests, matches CI
    ```

=== "Dependency refresh"

    ```bash
    make sync-dev  # upgrade lockfile, sync dev deps, refresh requirements files
    ```

=== "Docker deployment"

    ```bash
    make docker-build
    make docker-up
    make docker-logs
    ```

## Related

- How-to: [Prepare before committing](../how-to/prepare-commit.md)
- How-to: [Set up development environment](../how-to/setup-dev-environment.md)
