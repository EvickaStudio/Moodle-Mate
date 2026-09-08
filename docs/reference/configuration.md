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
- `TEMPERATURE` (float, default: `0.7`): Sampling temperature. Omitted for the
  original `gpt-5`, `gpt-5-mini`, and `gpt-5-nano` models and dated snapshots.
- `MAX_TOKENS` (int, default: `2048`): Completion token budget. For those GPT-5
  models this includes reasoning tokens; requests use minimal reasoning effort.
  An explicit smaller budget remains unchanged. If the model returns no text,
  summarization falls back to the original notification.
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

HTML exceeding 64 nesting levels or 10,000 parsed nodes is sent as plain text with
a formatting notice. The outgoing byte limit still applies. Failed sends remain
pending for retry, including when this fallback is used.

## Filters (`MOODLEMATE_FILTERS__*`)

- `IGNORE_SUBJECTS_CONTAINING` (list[string], default: empty): Subject substrings
  that cause a notification to be skipped.
- `IGNORE_COURSES_BY_ID` (list[int], default: empty): Skip notifications whose
  Moodle `courseid` matches an entry. Notifications without a course ID are kept.

## Health (`MOODLEMATE_HEALTH__*`)

- `ENABLED` (bool, default: `false`): Enable health notifications.
- `HEARTBEAT_INTERVAL` (int, optional): Hours between heartbeat messages.
- `FAILURE_ALERT_THRESHOLD` (int, optional): Consecutive errors before alert.
- `TARGET_PROVIDER` (string, optional): Provider name for health notifications.
- `FAILURE_ALERT_COOLDOWN` (int, default: `3600`): Minimum seconds between
  repeated outage alerts.
- `STALE_AFTER` (int, optional): Mark `/healthz` unhealthy after this many
  seconds without a successful Moodle poll. The default is the greater of
  three fetch intervals or 300 seconds.

## Web UI (`MOODLEMATE_WEB__*`)

Runtime settings updates take effect between notification batches. Provider
toggles and options, AI settings, and HTTP defaults update their active consumers.
An update can wait for an ongoing delivery or retry to finish. Changes apply only
to the running process; edit the environment configuration to retain them after
restart. Credentials, endpoints, and web server settings require a restart.

- `ENABLED` (bool, default: `true`): Enable the Web UI.
- `HOST` (string, default: `127.0.0.1`): Bind address (localhost only).
- `PORT` (int, default: `9095`): Bind port.
- `AUTH_SECRET` (string, required when `ENABLED=true`): Web UI login secret.

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

- `MOODLE_SESSION_FILE` (default: `moodle_session.json`): Encrypted cached session token file.
- `MOODLEMATE_SESSION_ENCRYPTION_KEY` (optional): Enables encrypted Moodle session caching when set.
- `MOODLE_STATE_FILE` (optional): Full path for `state.json`.
- `MOODLE_STATE_DIR` (default: `/app/state`): Directory for `state.json`.

A notification is complete only after all enabled providers confirm delivery.
Successful sends are saved immediately under `delivery_receipts` in `state.json`,
so retries and restarts skip those providers. Receipts are cleared when the
notification is checkpointed. Existing checkpoint-only state files remain
compatible, and test notifications always send again. A provider timeout with an
uncertain remote result can still cause duplicate delivery.
