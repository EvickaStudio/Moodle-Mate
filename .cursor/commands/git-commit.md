# Git Create Commit

## Overview

Create focused commits with clear messages and validated changes.

## Steps

1. Review working tree: `git status`, `git diff`; ensure changes are scoped.
2. Run relevant tests/commands for the changes (`pytest`, `uv run .\main.py` if needed).
3. Craft message `<type>(<scope>): <summary>` (<=72 chars, imperative); include issue key if applicable.
4. Avoid mixing formatting-only noise with functional changes; split if necessary.
5. Commit once satisfied; verify clean status.

## Checklist

- [ ] Diff reviewed and scoped.
- [ ] Tests/commands run for the change.
- [ ] Message follows format and length; scope/issue noted.
- [ ] No unrelated churn; working tree clean after commit.
