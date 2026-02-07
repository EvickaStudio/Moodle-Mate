# Security model notes

This document describes the current security posture and trade-offs in
Moodle Mate.

## Web UI access

The Web UI is intended for local access during development and small
self-hosted setups. It binds to `127.0.0.1` by default and is forced to
localhost at runtime. Authentication is required when Web UI is enabled and is
controlled by `MOODLEMATE_WEB__AUTH_SECRET`.

The UI uses random server-side session tokens (not raw passwords in cookies)
and CSRF protection for state-changing routes. If you expose the UI through a
reverse proxy, add TLS and an additional auth layer at the proxy boundary.

## Session caching

Moodle session caching is encrypted at rest and only enabled when
`MOODLEMATE_SESSION_ENCRYPTION_KEY` is set. The cache file is written with
restrictive permissions when possible.

If you enable session caching, place `MOODLE_SESSION_FILE` on a protected
filesystem and restrict backups for that path.
