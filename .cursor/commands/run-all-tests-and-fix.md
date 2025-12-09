# Run All Tests and Fix Failures

## Overview

Execute the suite, triage failures, and fix root causes with minimal changes.

## Steps

1. Run `pytest` (or targeted tests if faster); capture failures and stack traces.
2. Categorize failures: flaky vs new vs known; prioritize highest impact/root cause.
3. Fix one issue at a time; keep diffs small. Avoid real Moodle/API—mock externals.
4. Re-run affected tests (or full suite if small) to confirm fixes.
5. Note any remaining flakes/skips and create follow-ups if needed.

## Checklist

- [ ] Full or targeted tests run; failures captured.
- [ ] Failures categorized and addressed in priority order.
- [ ] External calls mocked; minimal, focused fixes.
- [ ] Tests re-run and passing; flakes/skips documented.
