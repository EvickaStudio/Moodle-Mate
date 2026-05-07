# Repository Guidelines

## Project Structure & Module Organization
- `main.py` is a thin entrypoint wrapper; the package entrypoint is `src/moodlemate/main.py`.
- `src/moodlemate/` contains application code: core utilities (`src/moodlemate/core`), domain modules (`src/moodlemate/moodle`, `src/moodlemate/ai`, `src/moodlemate/markdown`, `src/moodlemate/notifications`), providers (`src/moodlemate/providers`), and UI layers (`src/moodlemate/web`, `src/moodlemate/ui`).
- `tests/` holds pytest-based tests and shared fixtures in `tests/conftest.py`.
- `docs/` follows Diataxis (see `docs/README.md` for the map).
- `assets/` stores images and UI screenshots used by the README.

## Build, Test, and Development Commands
- `uv sync`: install runtime dependencies from `uv.lock`.
- `uv sync --extra dev`: install runtime + dev tooling.
- `uv run moodlemate` or `uv run python -m moodlemate`: run the app locally (starts the web dashboard by default).
- `docker compose build` / `docker compose up -d`: build and run the Docker image.
- `docker compose logs -f`: follow container logs.
- `uv run ruff format .` / `uv run ruff check --fix .`: format and lint.
- `uv run pyrefly check --summarize-errors` or `make typecheck`: static type check (`src/moodlemate/`; see `docs/pyrefly.md`).
- `make help`: list available project shortcuts.
- `make install-dev`, `make run`, `make test`, `make check`: common local workflows.
- `make clean`: remove `__pycache__` and bytecode files.

## Coding Style & Naming Conventions
- Python code uses 4-space indentation and PEP 8 conventions.
- Format and lint using Ruff (`make check`), which runs `ruff format` then `ruff check --fix`.
- File and module names are `snake_case`; classes use `CamelCase`.

## Testing Guidelines
- Tests use pytest and live under `tests/**/test_*.py`.
- Run all tests with `uv run pytest`.
- Coverage example: `uv run pytest --cov=src/moodlemate --cov-report=term-missing`.
- Add fixtures to `tests/conftest.py` when shared across modules.

## Commit & Pull Request Guidelines
- Recent commits follow a Conventional Commits style: `type(scope): short summary` (e.g., `feat(notification): ...`).
- Keep commits focused and descriptive; prefer imperative, present-tense summaries.
- PRs should include a short summary, linked issue (if applicable), and test results.
- For UI changes (web dashboard), include screenshots or a brief screen recording.

## Commit Workflow (Agents)
- Default working branch is `dev`; keep `main` release/stable.
- For feature work, create a short-lived branch (for example `feat/<name>` or `fix/<name>`).
- Feature branches must be merged into `dev` first.
- Only promote to `main` from `dev` via PR after `dev` has the approved changes.
- Use Conventional Commits only:
  - `fix:` = patch release
  - `feat:` = minor release
  - `type!:` or `BREAKING CHANGE:` = major release
  - `docs:`, `chore:`, `test:` usually do not trigger a release
- Group related changes into focused commits; avoid mixing unrelated refactors/docs/deps.
- Before committing, run:
  - `make check`
  - `make test`
  - `make typecheck` (or rely on `make ci-lint`, which includes Pyrefly)
- Push feature branches and open PRs against `dev`.
- Release promotion happens by merging `dev` into `main`, then running the release flow.

## Python Type Checking (Pyrefly)

This repository uses Pyrefly for static typing on application code (`src/moodlemate/`).

After Python changes under `src/moodlemate/`:

1. Run `make typecheck` (or `uv run pyrefly check --summarize-errors`) from the repo root.
2. Fix reported errors; prefer real fixes over new suppressions.
3. Do not add `# pyrefly: ignore` / `# type: ignore` or relax `[tool.pyrefly]` unless justified (false positive, untyped third-party boundary).

If import errors appear, verify `uv sync --extra dev`, then `[tool.pyrefly]` `search-path` / `project-includes` in `pyproject.toml`.

## Configuration & Security Notes
- Copy `example.env` to `.env` and set `MOODLEMATE_` variables (see `docs/how-to/setup-dev-environment.md`).
- Do not commit secrets or real Moodle credentials.
- Custom notification providers start from `src/moodlemate/templates/notification_service_template.py`.
