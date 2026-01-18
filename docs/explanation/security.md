# Security model notes

This document describes the current security posture and trade-offs in
Moodle Mate.

## Web UI access

The Web UI is intended for local access during development and small
self-hosted setups. It binds to `127.0.0.1` by default and is forced to
localhost at runtime. Authentication is a simple cookie check controlled by
`MOODLEMATE_WEB__AUTH_SECRET`.

This design favors low setup friction over strong authentication. If you
expose the UI through a reverse proxy, add TLS and an additional auth layer
at the proxy boundary.

## Session caching

The Moodle session cache persists the token and cookies to disk to keep the
app functional when Moodle logins are unreliable. This improves resilience
at the cost of storing sensitive material locally. The cache file is written
with restrictive permissions when possible.

If you want to reduce exposure, place `MOODLE_SESSION_FILE` on a protected
filesystem and restrict backups for that path.
