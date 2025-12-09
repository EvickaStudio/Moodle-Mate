# Generate PR Description

## Overview

Produce a clear PR summary that explains changes, risks, testing, and impacts.

## Steps

1. Summarize what changed and why; highlight behavior changes and affected areas.
2. List testing performed with commands (e.g., `pytest`, `uv run .\\main.py --test-notification`, targeted checks).
3. Note breaking changes or config/env impacts (.env keys, ports, migrations) and roll-back considerations.
4. Link related issues/tickets; mention follow-ups, known gaps, or TODOs.

## Checklist

- [ ] What/why articulated; behavior changes called out.
- [ ] Testing commands listed with outcomes.
- [ ] Config/env/breaking impacts noted; rollback/mitigation mentioned if relevant.
- [ ] Issues linked; follow-ups and gaps documented.
