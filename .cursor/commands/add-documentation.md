# Add Documentation

## Overview

Produce concise, useful docs when asked—prefer targeted docstrings over long prose.

## Steps

1. Identify what needs documenting (function/class/module/feature) and audience (dev/operator/user).
2. For code: add/refresh docstrings with purpose, params/returns, errors, side effects, brief example if non-trivial.
3. Keep README/docs updates minimal and only when requested; otherwise add short inline comments near complex logic.
4. Follow project style: Python, double quotes, type hints, no redundant narration; avoid leaking secrets/config.
5. If behavior changed, mention migration/compat impacts succinctly.

## Checklist

- [ ] Docstrings updated with purpose, params, returns, errors, side effects.
- [ ] Examples added only when needed; inline comments only for non-obvious logic.
- [ ] README/docs touched only if requested; no scope creep.
- [ ] Style aligned (double quotes, type hints); no secrets or credentials added.
