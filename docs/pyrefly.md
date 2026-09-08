# Pyrefly (static type checking)

Moodle Mate uses [Pyrefly](https://pyrefly.org/en/docs/) for static typing on **application code** under `src/moodlemate/`. Pyrefly does not replace Ruff (format/lint) or pytest (runtime tests).

## Local commands

```bash
uv sync --extra dev
uv run pyrefly check --summarize-errors
```

or `make typecheck` / `make typecheck-warnings` (`--min-severity warn`).

## Configuration

Sources of truth:

- `[tool.pyrefly]` and `[tool.pyrefly.errors]` in `pyproject.toml`
- `search-path = ["src"]` for resolving the `moodlemate` package
- `project-includes = ["src/moodlemate"]` — the `tests/` tree is **not** type-checked yet (many mocks/fixtures need explicit types or a baseline before turning that on).

Official reference: [Configuration](https://pyrefly.org/en/docs/configuration/).

## CI

GitHub Actions job `Lint, format, and type check (uv + Ruff + Pyrefly)` runs `make ci-lint`, which includes `pyrefly check --summarize-errors`.

For GitHub‑native annotations you can use the composite action documented at [Installation](https://pyrefly.org/en/docs/installation/) (`facebook/pyrefly`).

## Adopting stricter checks

- Migrate mypy/pyright settings with `uv run pyrefly init` and review generated config.
- For large legacy error sets, prefer a [baseline](https://pyrefly.org/en/docs/error-suppressions/) or targeted `# pyrefly: ignore[...]` over weakening global defaults.
- To type-check tests later: add `"tests"` to `project-includes`, then fix reported issues or baseline.

## pip installs

`requirements-dev.txt` contains pinned runtime and development dependencies with
hashes from `uv.lock`. After changing dependencies, update the lockfile and run
`scripts/export_requirements_dev.sh` or `make export-requirements-dev`.
