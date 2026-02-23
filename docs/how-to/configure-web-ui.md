# How to configure the Web UI

This guide enables and secures the built-in local Web UI.

## Important behavior

- Web UI requires `MOODLEMATE_WEB__AUTH_SECRET` when enabled.
- Host is forced to localhost at runtime (`127.0.0.1`) even if another host is configured.
- Login uses server-side session tokens and CSRF protection for state-changing requests.

## 1) Configure `.env`

```env
MOODLEMATE_WEB__ENABLED=true
MOODLEMATE_WEB__AUTH_SECRET=change-this-to-a-long-random-secret
MOODLEMATE_WEB__HOST=127.0.0.1
MOODLEMATE_WEB__PORT=9095
```

!!! warning

    Do not expose the Web UI directly to the public internet. If you proxy it, add TLS and another auth layer at the proxy.

## 2) Start the app

```bash
uv run moodlemate
```

## 3) Open the dashboard

Go to:

```text
http://127.0.0.1:9095
```

Log in with `MOODLEMATE_WEB__AUTH_SECRET`.

## 4) Use available endpoints

- `GET /api/status`
- `GET /api/history`
- `GET /api/config`
- `POST /api/config` (editable fields only)
- `POST /api/test-notification`
- `GET /healthz`

## Related

- Next: [Add custom provider](add-custom-provider.md)
- Explanation: [Security model](../explanation/security.md)
