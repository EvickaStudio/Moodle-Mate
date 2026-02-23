# Security model notes

This page summarizes the current security posture and practical limits.

## Web UI boundary

- Web UI requires `MOODLEMATE_WEB__AUTH_SECRET`.
- Web UI host is forced to `127.0.0.1` at runtime.
- Login creates random server-side session tokens.
- Cookies are `SameSite=strict`; auth cookie is `HttpOnly`.
- State-changing API routes require CSRF token validation.

## Configuration editing via Web UI

The dashboard supports runtime config updates, but selected sensitive/structural paths are immutable via API (for example Moodle credentials and provider secret endpoints/keys).

## Session and state files

- Moodle session cache is encrypted only when `MOODLEMATE_SESSION_ENCRYPTION_KEY` is set.
- Session file default: `moodle_session.json` (override with `MOODLE_SESSION_FILE`).
- State file is persisted with restrictive permissions where possible.

## Operational recommendations

1. Keep Web UI local-only (default behavior).
2. If reverse proxying, require TLS and independent upstream authentication.
3. Store `.env`, session cache, and state files on protected storage.
4. Limit backup/snapshot access to directories containing runtime secrets.

## Related

- [Configure Web UI](../how-to/configure-web-ui.md)
- [Configuration reference](../reference/configuration.md)
