# Lint Suite

## Overview

Format and lint the codebase consistently, fixing issues without noisy churn.

## Steps

1. Run formatting: `uvx ruff format .` (confirm allowed).
2. Run lint fixes: `uvx ruff check --fix .` (confirm allowed).
3. Manually address remaining warnings; avoid blanket ignores/`noqa` without justification.
4. Re-run checks to confirm clean; keep formatting-only diffs minimal in PRs.

## Checklist

- [ ] Formatting run (if permitted).
- [ ] Lint fixes applied; remaining warnings resolved manually.
- [ ] No unjustified ignores added.
- [ ] Final lint/format passes clean with minimal churn.
