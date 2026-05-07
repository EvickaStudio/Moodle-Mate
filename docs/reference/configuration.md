---
icon: material/cog-outline
description: All Moodle Mate environment variables, their types, defaults, and constraints.
---

# Configuration Reference

Moodle Mate reads configuration from:

- `.env` file in the project root
- Environment variables with the prefix `MOODLEMATE_`
- Nested fields use the `__` delimiter (e.g. `MOODLEMATE_NOTIFICATION__FETCH_INTERVAL=60`)

## Moodle (`MOODLEMATE_MOODLE__*`)

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `URL` | string | _(required)_ | Base URL of your Moodle instance |
| `USERNAME` | string | _(required)_ | Moodle login username |
| `PASSWORD` | string | _(required)_ | Moodle login password |
| `INITIAL_FETCH_COUNT` | int | `1` | Number of notifications to fetch on first run |

## AI (`MOODLEMATE_AI__*`)

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `ENABLED` | bool | `true` | Enable AI summarisation |
| `API_KEY` | string | `""` | API key for the AI provider |
| `MODEL` | string | `gpt-5-nano` | Model identifier |
| `TEMPERATURE` | float | `0.7` | Sampling temperature |
| `MAX_TOKENS` | int | `150` | Maximum summary tokens |
| `SYSTEM_PROMPT` | string | built-in | Override the summarisation system prompt |
| `ENDPOINT` | string | `null` | Optional custom API endpoint (for OpenAI-compatible APIs) |

## Notifications (`MOODLEMATE_NOTIFICATION__*`)

| Variable | Type | Default | Range | Notes |
|----------|------|---------|-------|-------|
| `FETCH_INTERVAL` | int | `60` | `10–3600` | Polling interval in seconds |
| `MAX_RETRIES` | int | `5` | `0–10` | Max delivery retries per provider |
| `CONNECT_TIMEOUT` | float | `10.0` | `(0, 60]` | HTTP connect timeout in seconds |
| `READ_TIMEOUT` | float | `30.0` | `(0, 180]` | HTTP read timeout in seconds |
| `RETRY_TOTAL` | int | `3` | `0–10` | Total HTTP retries |
| `RETRY_BACKOFF_FACTOR` | float | `1.0` | `0.0–5.0` | Backoff multiplier between retries |
| `MAX_PAYLOAD_BYTES` | int | `65536` | `1024–262144` | Maximum notification payload size |

## Filters (`MOODLEMATE_FILTERS__*`)

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `IGNORE_SUBJECTS_CONTAINING` | list[string] | `[]` | Drop notifications whose subject contains any of these strings |
| `IGNORE_COURSES_BY_ID` | list[int] | `[]` | Drop all notifications from these Moodle course IDs |

!!! warning "Filters are not yet fully implemented"
    The filter fields exist in the config model but course/subject filtering is still a work in progress.

## Health (`MOODLEMATE_HEALTH__*`)

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `ENABLED` | bool | `false` | Enable health monitoring |
| `HEARTBEAT_INTERVAL` | int | `null` | Hours between heartbeat notifications (optional) |
| `FAILURE_ALERT_THRESHOLD` | int | `null` | Error count before an alert is fired (optional) |
| `TARGET_PROVIDER` | string | `null` | Which enabled provider to send health alerts through |

## Web UI (`MOODLEMATE_WEB__*`)

| Variable | Type | Default | Notes |
|----------|------|---------|-------|
| `ENABLED` | bool | `true` | Enable the local Web UI |
| `HOST` | string | `127.0.0.1` | Overridden to `127.0.0.1` at runtime regardless |
| `PORT` | int | `9095` | HTTP port |
| `AUTH_SECRET` | string | `null` | **Required when Web UI is enabled.** App refuses to start without it. |

!!! note "Localhost-only enforcement"
    The Web UI always binds to `127.0.0.1` at runtime, even if you configure a different host.
    See the [security model](../explanation/security.md) for details.

## Built-in providers

All provider config blocks have `ENABLED` (bool, default `false`).

### Discord (`MOODLEMATE_DISCORD__*`)

| Variable | Type | Default |
|----------|------|---------|
| `ENABLED` | bool | `false` |
| `WEBHOOK_URL` | string | `""` |
| `BOT_NAME` | string | `MoodleMate` |
| `THUMBNAIL_URL` | string | `""` |

### Pushbullet (`MOODLEMATE_PUSHBULLET__*`)

| Variable | Type | Default |
|----------|------|---------|
| `ENABLED` | bool | `false` |
| `API_KEY` | string | `""` |
| `INCLUDE_SUMMARY` | bool | `true` |

### Webhook.site (`MOODLEMATE_WEBHOOK_SITE__*`)

| Variable | Type | Default |
|----------|------|---------|
| `ENABLED` | bool | `false` |
| `WEBHOOK_URL` | string | `""` |
| `INCLUDE_SUMMARY` | bool | `true` |

## Custom providers

Follow the pattern `MOODLEMATE_<PROVIDER_NAME>__<FIELD_NAME>`. The provider name
must match both the `Settings` field and the provider folder name.

See [Add a custom provider](../how-to/add-custom-provider.md) for a full walkthrough.

## Runtime / session variables

!!! important "Different prefix"
    The variables below are read **directly from the environment** and do **not** use the
    `MOODLEMATE_` prefix or nested `__` delimiter.

| Variable | Default | Notes |
|----------|---------|-------|
| `MOODLEMATE_SESSION_ENCRYPTION_KEY` | `null` | Enables Fernet-encrypted Moodle session cache |
| `MOODLE_SESSION_FILE` | `moodle_session.json` | Path for the (possibly encrypted) session cache file |
| `MOODLE_STATE_FILE` | _(unset)_ | Explicit path for `state.json` |
| `MOODLE_STATE_DIR` | _(unset)_ | Directory that contains `state.json` |

If neither `MOODLE_STATE_FILE` nor `MOODLE_STATE_DIR` is set and `/app/state` does not exist,
the fallback is a local `./state.json` in the working directory.

## Related

- [CLI reference](cli.md)
- [Add a custom provider guide](../how-to/add-custom-provider.md)
