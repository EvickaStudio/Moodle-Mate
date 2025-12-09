# Fix Git Issues

## Overview

Resolve conflicts and history problems safely without losing user changes.

## Steps

1. For conflicts: inspect both sides, choose correct code, rerun impacted tests.
2. Prefer rebase/cherry-pick for history fixes; avoid force-push unless approved.
3. Explain each git command before running; ensure working tree is clean.
4. Never drop user changes without confirmation; stash/backup if unsure.

## Checklist

- [ ] Conflicts resolved with intent preserved; tests run if impacted.
- [ ] History fixes use rebase/cherry-pick; force-push avoided/approved.
- [ ] Commands explained; working tree clean.
- [ ] User changes safeguarded (no unintended drops).
