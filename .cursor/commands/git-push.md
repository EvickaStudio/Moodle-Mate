# Git Push

## Overview

Push clean, tested branches while keeping history tidy and conflicts minimal.

## Steps

1. Fetch and rebase onto main when practical; resolve conflicts locally.
2. Ensure working tree is clean; tests pass (`pytest`/targeted).
3. Push with `git push -u origin HEAD`; avoid force-push unless approved.
4. If rejected, prefer rebase over merge unless user requests otherwise.

## Checklist

- [ ] Rebased on main (if applicable); conflicts resolved.
- [ ] Tests pass; working tree clean.
- [ ] Pushed with `git push -u origin HEAD`; force-push avoided/approved.
- [ ] Remote rejects handled via rebase unless directed otherwise.
