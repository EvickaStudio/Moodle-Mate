# Configuration Reference

This reference lists settings read from `.env` or environment variables with the
`MOODLEMATE_` prefix and `__` nested delimiter.

## Moodle (`MOODLEMATE_MOODLE__*`)

- `URL` (required, string): Base Moodle URL, e.g. `https://moodle.example.edu`.
- `USERNAME` (required, string): Moodle username.
- `PASSWORD` (required, string): Moodle password.
- `INITIAL_FETCH_COUNT` (int, default: `1`): Number of newest notifications to
  select on the first run when no state file exists. The oldest selected ID is
  saved before delivery. Retries keep that window even if newer messages arrive
  or the fetch count changes; the successful-delivery checkpoint advances only
  after delivery or an intentional filter skip.

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

Custom OpenAI-compatible endpoints accept their own key format. Set `API_KEY`
to an empty string only when the custom server does not require authentication;
requests then omit the Authorization header. The default OpenAI endpoint still
requires an OpenAI key. Use the server's API base URL, typically ending in `/v1`.

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

Heartbeat and alert timers advance only after the target provider confirms delivery.
Failed sends are retried on a later polling cycle; recovery announcements remain
pending until delivered. Heartbeats report whether Moodle polling has succeeded.

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
- `HOST` (string, default: `127.0.0.1`): Bind address. Docker uses `0.0.0.0`
  inside the container; Compose publishes the configured port on host localhost.
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

The `MOODLE_` path variables are read directly from the process environment.
For native runs, adding them to `.env` alone does not export them. Set them in
the launching shell or service configuration, for example on Linux/macOS:

```bash
export MOODLE_STATE_DIR="$PWD/state"
export MOODLE_SESSION_FILE="$MOODLE_STATE_DIR/moodle_session.json"
export MOODLE_LOG_DIR="$PWD/logs"
uv run moodlemate
```

Docker Compose loads `.env` into the container environment through `env_file`;
its explicit `environment` entries take precedence. Paths used there refer to
the container filesystem. Mount those directories to retain files on the host.

- `MOODLE_SESSION_FILE` (native default: `moodle_session.json`; Docker default: `$MOODLE_STATE_DIR/moodle_session.json`): Encrypted cached session token file.
- `MOODLE_LOG_DIR` (native default: `logs`; Docker default: `/app/logs`): Directory for rotating log files.
- `MOODLE_STATE_FILE` (optional): Full path for `state.json`.
- `MOODLE_STATE_DIR` (optional): Directory for `state.json`, unless `MOODLE_STATE_FILE`
  is set. Docker defaults to `/app/state`. Native runs use `/app/state` when it
  exists, otherwise `state.json` in the working directory.

`MOODLEMATE_SESSION_ENCRYPTION_KEY` enables encrypted Moodle session caching when
set. This setting uses the `MOODLEMATE_` prefix and is loaded from `.env` for native
runs as well as from environment variables. The path variables do not enable
session caching by themselves.

A notification is complete only after all enabled providers confirm delivery.
Successful sends are saved immediately under `delivery_receipts` in `state.json`,
so retries and restarts skip those providers. Receipts are cleared when the
notification is checkpointed. Existing checkpoint-only state files remain
compatible, and test notifications always send again. A provider timeout with an
uncertain remote result can still cause duplicate delivery.
