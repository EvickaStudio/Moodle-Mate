---
icon: material/console
description: Moodle Mate CLI entrypoints and supported command-line options.
---

# CLI Reference

## Entrypoints

Moodle Mate exposes a single entrypoint defined in `pyproject.toml`:

```bash
uv run moodlemate          # via project script
uv run python -m moodlemate  # as a Python module
```

Both execute `moodlemate.main:main`.

## Quick help

```bash
uv run moodlemate --help
```

## Options

### `--test-notification`

Sends one test notification through every currently enabled provider, then exits.
Use this to verify your configuration is correct without waiting for a real Moodle notification.

```bash
uv run moodlemate --test-notification
```

!!! tip
    This is equivalent to running `make test-notification`.

## Startup behavior

On every start (including `--test-notification`), Moodle Mate:

1. Initialises logging.
2. Prints the Moodle Mate logo.
3. Loads and validates `Settings` from `.env` / environment.
4. Configures HTTP connection management (timeouts, retries).
5. Initialises the state manager, Moodle API client, AI summariser (if enabled), and providers.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Clean exit (normal interrupt or `--test-notification` completed) |
| `1` | Configuration failed to load, or a fatal startup error was raised |

## Related

- [Configuration reference](configuration.md)
- [Make targets reference](make-targets.md)
