# Debug Issue

## Overview

Reproduce, diagnose, and fix issues with minimal, targeted changes and verification.

## Steps

1. Capture expected vs actual, repro steps, inputs/config (.env), and logs/tracebacks.
2. Inspect recent changes and failure surface (notification flow, Moodle API, providers, state persistence).
3. Add minimal logging with `logging` (no prints) around failure points; avoid noisy loops.
4. Check network/timeouts, Moodle responses, credentials, session refresh; validate retry/backoff paths.
5. Propose the smallest safe fix; consider impact on notification delivery/duplication and state.
6. Add prevention (tests/guards); verify with `pytest` or focused checks.

## Checklist

- [ ] Repro steps and context captured (inputs, env, logs).
- [ ] Root cause identified; minimal logging added if needed.
- [ ] Fix applied with awareness of notification/state side effects.
- [ ] Tests/targeted checks run; prevention added where practical.
