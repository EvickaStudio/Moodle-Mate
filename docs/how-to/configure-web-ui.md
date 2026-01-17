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
