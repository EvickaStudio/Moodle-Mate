# How to set up a local development environment

This guide sets up Moodle Mate for local development and testing.

## Prerequisites

- Python `3.11+`
- `uv` installed
- Project cloned locally

## Recommended path (uv)

1. Install runtime + dev dependencies:

   ```bash
   uv sync --extra dev
   ```

2. Run the app:

   ```bash
   uv run moodlemate
   ```

3. Run tests and checks:

   ```bash
   make test
   make check
   ```

!!! tip

    `make ci-local` runs the same lint/test checks used in CI workflows.

## Alternative path (venv + pip)

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
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt -r requirements-dev.txt
    python -m moodlemate
    ```

## Verify installation

Run:

```bash
uv run moodlemate --test-notification
```

If provider credentials are configured and at least one provider is enabled, a test notification is sent.

## Related

- Next: [Configure Web UI](configure-web-ui.md)
- Before pushing: [Prepare changes before committing](prepare-commit.md)
- Reference: [Configuration](../reference/configuration.md)
