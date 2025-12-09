# Fix Compile Errors

## Overview

Resolve syntax/import/type/reference errors at the source and verify the fix.

## Steps

1. Identify failing file/line from traceback or lint output.
2. Fix root cause (imports, names, types); avoid broad try/except or ignores.
3. Keep style: PEP 8, double quotes, explicit imports, no unused deps.
4. Re-run the failing command/test (`uv run .\main.py` or `pytest` as appropriate).

## Checklist

- [ ] Error location understood (trace/lint).
- [ ] Root cause fixed without masking errors.
- [ ] Style preserved; imports explicit and used.
- [ ] Failing command/test re-run and passes.
