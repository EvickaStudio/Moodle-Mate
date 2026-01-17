# Configuration Reference

This reference lists settings read from `.env` or environment variables with the
`MOODLEMATE_` prefix and `__` nested delimiter.

## Moodle (`MOODLEMATE_MOODLE__*`)

- `URL` (required, string): Base Moodle URL, e.g. `https://moodle.example.edu`.
- `USERNAME` (required, string): Moodle username.
- `PASSWORD` (required, string): Moodle password.
- `INITIAL_FETCH_COUNT` (int, default: `1`): Number of newest notifications to
  process on the first run when no state file exists.

## AI (`MOODLEMATE_AI__*`)

- `ENABLED` (bool, default: `true`): Enable AI summaries.
- `API_KEY` (string, default: empty): Provider API key.
- `MODEL` (string, default: `gpt-5-nano`): Model name.
- `TEMPERATURE` (float, default: `0.7`): Sampling temperature.
- `MAX_TOKENS` (int, default: `150`): Maximum summary tokens.
- `SYSTEM_PROMPT` (string, default: set): System prompt for the summarizer.
- `ENDPOINT` (string, optional): Custom API endpoint.

## Notifications (`MOODLEMATE_NOTIFICATION__*`)

- `MAX_RETRIES` (int, default: `5`): Max consecutive fetch errors before reset.
- `FETCH_INTERVAL` (int, default: `60`): Seconds between fetch attempts.
- `CONNECT_TIMEOUT` (float, default: `10.0`): HTTP connect timeout.
- `READ_TIMEOUT` (float, default: `30.0`): HTTP read timeout.
- `RETRY_TOTAL` (int, default: `3`): HTTP retry attempts.
- `RETRY_BACKOFF_FACTOR` (float, default: `1.0`): HTTP backoff factor.
- `MAX_PAYLOAD_BYTES` (int, default: `65536`): Max bytes per message/summary.

## Filters (`MOODLEMATE_FILTERS__*`)

- `IGNORE_SUBJECTS_CONTAINING` (list[string], default: empty): Subject substrings
  that cause a notification to be skipped.
- `IGNORE_COURSES_BY_ID` (list[int], default: empty): Reserved for future course
  filtering.

## Health (`MOODLEMATE_HEALTH__*`)

- `ENABLED` (bool, default: `false`): Enable health notifications.
- `HEARTBEAT_INTERVAL` (int, optional): Hours between heartbeat messages.
- `FAILURE_ALERT_THRESHOLD` (int, optional): Consecutive errors before alert.
- `TARGET_PROVIDER` (string, optional): Provider name for health notifications.

## Web UI (`MOODLEMATE_WEB__*`)

- `ENABLED` (bool, default: `true`): Enable the Web UI.
- `HOST` (string, default: `127.0.0.1`): Bind address (localhost only).
- `PORT` (int, default: `9095`): Bind port.
- `AUTH_SECRET` (string, optional): Enables Web UI auth when set.

## Providers (`MOODLEMATE_<PROVIDER>__*`)

All providers support:

- `ENABLED` (bool, default: `false`)

### Discord (`MOODLEMATE_DISCORD__*`)

- `WEBHOOK_URL` (string): Discord webhook URL.
- `BOT_NAME` (string, default: `MoodleMate`)
- `THUMBNAIL_URL` (string, optional)

### Pushbullet (`MOODLEMATE_PUSHBULLET__*`)

- `API_KEY` (string)
- `INCLUDE_SUMMARY` (bool, default: `true`)

### Webhook.site (`MOODLEMATE_WEBHOOK_SITE__*`)

- `WEBHOOK_URL` (string)
- `INCLUDE_SUMMARY` (bool, default: `true`)

### Custom providers

Custom providers use the same pattern:

- `MOODLEMATE_<PROVIDER_NAME>__<FIELD_NAME>`

## Runtime files and paths

These are read directly from the environment:

- `MOODLE_SESSION_FILE` (default: `moodle_session.json`): Cached session token.
- `MOODLE_STATE_FILE` (optional): Full path for `state.json`.
- `MOODLE_STATE_DIR` (default: `/app/state`): Directory for `state.json`.
