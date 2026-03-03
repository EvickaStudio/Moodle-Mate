# Configuration Reference

Moodle Mate reads configuration from:

- `.env`
- environment variables with prefix `MOODLEMATE_`
- nested fields via `__` delimiter

Example: `MOODLEMATE_NOTIFICATION__FETCH_INTERVAL=60`

## Moodle (`MOODLEMATE_MOODLE__*`)

- `URL` (required, string)
- `USERNAME` (required, string)
- `PASSWORD` (required, string)
- `INITIAL_FETCH_COUNT` (int, default `1`)

## AI (`MOODLEMATE_AI__*`)

- `ENABLED` (bool, default `true`)
- `API_KEY` (string, default empty)
- `MODEL` (string, default `gpt-5-nano`)
- `TEMPERATURE` (float, default `0.7`)
- `MAX_TOKENS` (int, default `150`)
- `SYSTEM_PROMPT` (string, default built-in summarizer prompt)
- `ENDPOINT` (string, optional)

## Notifications (`MOODLEMATE_NOTIFICATION__*`)

- `MAX_RETRIES` (int, default `5`, range `0..10`)
- `FETCH_INTERVAL` (int, default `60`, range `10..3600`)
- `CONNECT_TIMEOUT` (float, default `10.0`, range `(0, 60]`)
- `READ_TIMEOUT` (float, default `30.0`, range `(0, 180]`)
- `RETRY_TOTAL` (int, default `3`, range `0..10`)
- `RETRY_BACKOFF_FACTOR` (float, default `1.0`, range `0.0..5.0`)
- `MAX_PAYLOAD_BYTES` (int, default `65536`, range `1024..262144`)

## Filters (`MOODLEMATE_FILTERS__*`)

- `IGNORE_SUBJECTS_CONTAINING` (list[string], default empty)
- `IGNORE_COURSES_BY_ID` (list[int], default empty)

## Health (`MOODLEMATE_HEALTH__*`)

- `ENABLED` (bool, default `false`)
- `HEARTBEAT_INTERVAL` (int, optional, in hours)
- `FAILURE_ALERT_THRESHOLD` (int, optional)
- `TARGET_PROVIDER` (string, optional)

## Web UI (`MOODLEMATE_WEB__*`)

- `ENABLED` (bool, default `true`)
- `HOST` (string, default `127.0.0.1`)
- `PORT` (int, default `9095`)
- `AUTH_SECRET` (string, required when Web UI is enabled)

!!! note

    Runtime forces Web UI binding to `127.0.0.1` for localhost-only operation.

## Built-in providers

All providers use `ENABLED` (bool, default `false`).

### Discord (`MOODLEMATE_DISCORD__*`)

- `WEBHOOK_URL` (string)
- `BOT_NAME` (string, default `MoodleMate`)
- `THUMBNAIL_URL` (string, default empty)

### Pushbullet (`MOODLEMATE_PUSHBULLET__*`)

- `API_KEY` (string)
- `INCLUDE_SUMMARY` (bool, default `true`)

### Webhook.site (`MOODLEMATE_WEBHOOK_SITE__*`)

- `WEBHOOK_URL` (string)
- `INCLUDE_SUMMARY` (bool, default `true`)

## Custom providers

Pattern:

- `MOODLEMATE_<PROVIDER_NAME>__<FIELD_NAME>`

`<PROVIDER_NAME>` must match the `Settings` field and provider folder name.

## Runtime/state/session variables

These are read directly from the environment (outside the `MOODLEMATE_` nested model):

- `MOODLEMATE_SESSION_ENCRYPTION_KEY` (optional): enables encrypted Moodle session cache.
- `MOODLE_SESSION_FILE` (default `moodle_session.json`): path for encrypted session cache file.
- `MOODLE_STATE_FILE` (optional): explicit path for state file.
- `MOODLE_STATE_DIR` (optional): directory for `state.json`.

If neither `MOODLE_STATE_FILE` nor `MOODLE_STATE_DIR` is set and `/app/state` does not exist, fallback is local `./state.json`.

## Related

- [CLI reference](cli.md)
- [Add custom provider guide](../how-to/add-custom-provider.md)
