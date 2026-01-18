# How to set up a local dev environment

This guide shows you how to prepare a local environment for development.

## Steps (uv recommended)

1. From the repo root, install dependencies:

   ```bash
   uv sync --extra dev
   ```

2. Run the app or the test suite:

   ```bash
   uv run moodlemate
   uv run pytest
   ```

## Steps (manual venv)

1. Create and activate a virtual environment.

   Windows:

   ```powershell
   py -m venv venv
   venv\Scripts\activate
   ```

   Linux / macOS:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies and run:

   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   python -m moodlemate
   ```
