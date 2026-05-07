---
icon: material/monitor-lock
description: Enable, secure, and access the Moodle Mate local Web UI.
---

# How to configure the Web UI

Moodle Mate ships with a local FastAPI-based dashboard for monitoring status,
viewing notification history, and tweaking runtime configuration — without restarting the app.

## Security boundaries

!!! danger "Do not expose the Web UI to the internet"
    The server **always** binds to `127.0.0.1` at runtime, even if you configure a different host.
    If you reverse-proxy it, you **must** add TLS and an independent authentication layer at the proxy.

- The host is forced to `127.0.0.1` at runtime regardless of the configured value.
- `MOODLEMATE_WEB__AUTH_SECRET` is required — the server refuses to start without it.
- Login creates a random server-side session token (30-day max-age cookie).
- Cookies are `SameSite=strict`; the auth cookie is `HttpOnly`.
- All state-changing API routes require a CSRF token (`X-CSRF-Token` header).
- Login attempts are rate-limited per client IP.

## 1 — Configure `.env`

```env title=".env"
MOODLEMATE_WEB__ENABLED=true
MOODLEMATE_WEB__AUTH_SECRET=change-this-to-a-long-random-secret  # (1)!
MOODLEMATE_WEB__HOST=127.0.0.1
MOODLEMATE_WEB__PORT=9095
```

1.  Generate a strong random secret, for example with:
    `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## 2 — Start the app

```bash
uv run moodlemate
```

## 3 — Open the dashboard

Navigate to:

```text
http://127.0.0.1:9095
```

Log in using the value of `MOODLEMATE_WEB__AUTH_SECRET` as the password.

## 4 — Available endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/` | ✅ | Dashboard UI |
| `GET` | `/login` | — | Login page |
| `POST` | `/api/login` | CSRF | Authenticate and receive a session cookie |
| `POST` | `/api/logout` | ✅ CSRF | Invalidate the current session |
| `GET` | `/api/status` | ✅ | App running state and last notification ID |
| `GET` | `/api/history` | ✅ | In-memory recent notification history |
| `GET` | `/api/config` | ✅ | Current configuration (sensitive fields redacted) |
| `POST` | `/api/config` | ✅ CSRF | Update mutable runtime configuration fields |
| `POST` | `/api/test-notification` | ✅ CSRF | Trigger a test notification via all enabled providers |
| `GET` | `/healthz` | — | Health probe (no auth required) |

!!! note "Immutable fields via API"
    Sensitive or structural fields cannot be changed via `POST /api/config` — this includes
    Moodle credentials, provider webhook URLs and API keys, and all Web UI settings.
    Restart the app with an updated `.env` to change these.

## Related

- Next: [Add a custom provider](add-custom-provider.md)
- Explanation: [Security model](../explanation/security.md)
- Reference: [Configuration](../reference/configuration.md)
