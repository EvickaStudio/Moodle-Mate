# Clarify Task

## Overview

Quickly align on scope, constraints, and success criteria before writing code or docs.

## Steps

1. Restate the request in your own words: what to change, what to avoid, expected outputs (code, tests, docs).
2. Ask 2-3 focused, multiple-choice questions covering:
   - Data flow/APIs/auth, Moodle endpoints, provider targets (Discord/webhook/etc.).
   - Config inputs (env keys, URLs, credentials presence), feature flags, timeouts.
   - Edge cases (dup notifications, retries, rate limits, disk persistence).
3. Confirm allowed commands/tools and runtime: `uv run .\main.py`, `pytest`, docker/compose, network expectations.
4. Call out constraints: performance, security, no new deps, downtime tolerance, logging requirements.
5. Wait for user confirmation before implementing.

## Checklist

- [ ] Request restated with scope and deliverables.
- [ ] 2-3 multiple-choice questions asked (APIs/auth, config, edge cases).
- [ ] Allowed commands/tools and constraints confirmed.
- [ ] No coding started before confirmation.
