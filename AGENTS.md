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
- `./cleaner.sh`: remove `__pycache__` and bytecode files.

## Coding Style & Naming Conventions
- Python code uses 4-space indentation and PEP 8 conventions.
- Format and lint using Ruff (`./format.sh`), which runs `ruff format` then `ruff check --fix`.
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

## Configuration & Security Notes
- Copy `example.env` to `.env` and set `MOODLEMATE_` variables (see `docs/how-to/setup-dev-environment.md`).
- Do not commit secrets or real Moodle credentials.
- Custom notification providers start from `src/moodlemate/templates/notification_service_template.py`.
