# How to configure the Web UI

This guide shows you how to enable and access the Web UI locally.

## Steps

1. Set Web UI settings in your `.env`:

   ```env
   MOODLEMATE_WEB__ENABLED=1
   MOODLEMATE_WEB__AUTH_SECRET=your_long_password
   MOODLEMATE_WEB__PORT=9095
   ```

2. Start the app:

   ```bash
   uv run moodlemate
   ```

3. Open the dashboard in your browser:

   ```
   http://127.0.0.1:9095
   ```

4. Log in using the value of `MOODLEMATE_WEB__AUTH_SECRET`.

## Docker

`docker compose up -d` publishes the dashboard on host localhost using
`MOODLEMATE_WEB__PORT` (default `9095`). The container listens on `0.0.0.0`;
authentication and CSRF protection still apply. For a manual `docker run`, publish
the port explicitly with `-p 127.0.0.1:9095:9095`.

Run `python scripts/smoke_docker.py` to build and test an isolated container with
dummy Moodle responses, without mounting your configuration or state.
