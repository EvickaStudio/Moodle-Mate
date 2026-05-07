---
icon: material/hammer-wrench
description: Install Moodle Mate dependencies and run the app or tests locally.
---

# How to set up a local development environment

This guide gets Moodle Mate running on your machine for development and testing.

## Prerequisites

- Python `3.11` or later
- [`uv`](https://astral.sh/uv) — the project's package manager
- The repository cloned locally

## Recommended path — `uv`

=== "Install & run"

    ```bash
    # Install runtime + dev dependencies
    uv sync --extra dev

    # Run the application
    uv run moodlemate
    ```

=== "Run tests & checks"

    ```bash
    make test     # pytest
    make check    # ruff format + ruff lint --fix
    ```

=== "Full CI suite"

    ```bash
    make ci-local  # non-mutating lint + tests, matches CI
    ```

!!! tip "`make bootstrap` is an alias"
    `make bootstrap` does the same thing as `make install-dev` — installs runtime and dev
    dependencies in one command.

## Alternative path — `venv` + `pip`

=== "Linux / macOS"

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt
    python -m moodlemate
    ```

=== "Windows (PowerShell)"

    ```powershell
    py -m venv venv
    .\\venv\\Scripts\\Activate.ps1
    pip install -r requirements.txt -r requirements-dev.txt
    python -m moodlemate
    ```

## Verify installation

```bash
uv run moodlemate --test-notification
```

If at least one provider is enabled and credentials are correct, a test notification is sent
and logged. If no providers are enabled, a warning is logged — that is expected.

## Serving the documentation locally

```bash
uv run mkdocs serve
```

The docs site is served at `http://127.0.0.1:8000` with live reload on file changes.

## Related

- Next: [Configure Web UI](configure-web-ui.md)
- Before pushing: [Prepare before committing](prepare-commit.md)
- Full command list: [Make targets reference](../reference/make-targets.md)
