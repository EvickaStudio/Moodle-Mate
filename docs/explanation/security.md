---
icon: material/shield-check
description: Web UI security boundaries, session handling, and operational security guidance.
---

# Security model

This page describes the current security posture and its practical limits.

## Web UI boundary

The Web UI is designed to be a **localhost-only** operator tool, not a public-facing service.

| Control | Detail |
|---------|--------|
| Binding | Always `127.0.0.1`, enforced at runtime — cannot be overridden via config |
| Authentication required | `MOODLEMATE_WEB__AUTH_SECRET` must be set; app refuses to start without it |
| Session tokens | Random `secrets.token_urlsafe(32)` values stored server-side |
| Session lifetime | 30-day max-age cookie |
| Cookie flags | `SameSite=strict`; auth cookie is `HttpOnly` |
| CSRF protection | All state-changing routes require `X-CSRF-Token` header matching CSRF cookie |
| Rate limiting | Login endpoint is rate-limited per client IP |

## Configuration editing via Web UI

The dashboard allows runtime config updates, but a fixed set of sensitive and structural paths
are **immutable via the API**:

- Moodle credentials (`url`, `username`, `password`)
- AI API key and endpoint
- Provider webhook URLs and API keys
- Web UI settings (`enabled`, `host`, `port`, `auth_secret`)

To change these, update `.env` and restart the app.

## Session and state files

| File | Encryption | Override |
|------|------------|---------|
| `moodle_session.json` | Fernet-encrypted when `MOODLEMATE_SESSION_ENCRYPTION_KEY` is set; plaintext otherwise | `MOODLE_SESSION_FILE` env var |
| `state.json` | Not encrypted (contains only the last notification ID and recent history) | `MOODLE_STATE_FILE` or `MOODLE_STATE_DIR` env var |

Files are written with restrictive permissions where the OS allows it.

## Operational recommendations

- [x] Keep the Web UI local-only (default behaviour — no action required).
- [x] Store `.env`, session cache, and state files on protected storage.
- [x] Limit backup/snapshot access to directories containing runtime secrets.
- [ ] If reverse proxying, require TLS and independent upstream authentication at the proxy.
- [ ] Set `MOODLEMATE_SESSION_ENCRYPTION_KEY` to enable encrypted session caching.

## Related

- [Configure Web UI](../how-to/configure-web-ui.md)
- [Configuration reference](../reference/configuration.md)
