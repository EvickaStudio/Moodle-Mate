# Docker Logs Tail

## Overview

Inspect container logs quickly with the right filters (name, tail, since, errors).

## Steps

1. List containers: `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"`.
2. Ask which container(s) and filters (tail N, since, errors only, timestamps).
3. Tail logs: `docker logs -f --tail 200 <name>` (add `--timestamps` or `--since` as needed).
4. For compose: `docker compose logs -f --tail 200 <service>`.
5. Stop tailing when done to avoid noise.

## Checklist

- [ ] Container(s) identified and filters confirmed.
- [ ] Correct tail command used (with timestamps/since if requested).
- [ ] Output reviewed for errors/restarts/tracebacks.
- [ ] Tail stopped after inspection.
