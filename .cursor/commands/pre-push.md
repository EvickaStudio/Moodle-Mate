# Pre Push

## Overview

Run local checks (format, lint with fixes, regenerate requirements, tests) before pushing. Do not push via git command from the agent.

## Steps

1. Sync deps: `uv sync`.
2. Format: `uvx ruff format .` (auto-fix).
3. Lint with fixes: `uvx ruff check --fix .` (rerun without `--fix` if needed).
4. Regenerate requirements: `uv pip compile pyproject.toml -o requirements.txt`.
5. Run tests (CI-like): `uv run pytest -q` (or targeted if faster).
6. Optional sanity: `uv run python -m compileall src` for bytecode check.
7. Review `git status` / `git diff`; push manually outside this command.

## Checklist

- [ ] `uv sync` completed.
- [ ] Formatting applied (`uvx ruff format .`).
- [ ] Lint fixed or clean (`uvx ruff check --fix .`).
- [ ] `requirements.txt` regenerated.
- [ ] Tests run and passing (`uv run pytest -q`).
- [ ] Working tree reviewed; ready to push manually.
