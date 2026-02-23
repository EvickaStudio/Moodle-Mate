# CLI Reference

## Entrypoints

- `uv run moodlemate`
- `uv run python -m moodlemate`

Both run the same package entrypoint (`moodlemate.main:main`).

## Options

### `--test-notification`

Sends one test notification through all currently enabled providers, then exits.

```bash
uv run moodlemate --test-notification
```

## Exit behavior

- Exits with non-zero status if configuration loading or startup fails.
- Normal runtime continues until interrupted.

## Related

- See [Configuration reference](configuration.md) for required variables.
