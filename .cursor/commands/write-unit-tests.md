# Write Unit Tests

## Overview

Add deterministic pytest coverage for happy paths and edge/error cases without real network calls.

## Steps

1. Identify behavior to cover (success, failure, edge cases). Name tests clearly.
2. Mock network/Moodle/API/HTTP—no real calls. Use fixtures/fakes; avoid sleeps.
3. Reset global/singleton state as needed (e.g., `StateManager`) to keep tests isolated.
4. Use Arrange-Act-Assert; assert logs/errors where relevant.
5. Run `pytest` (targeted if faster); keep tests deterministic.

## Checklist

- [ ] Happy, edge, and failure cases covered.
- [ ] External calls mocked; no real network.
- [ ] State isolated/reset; no cross-test leakage.
- [ ] Assertions meaningful (results, logs/errors); pytest run passes.
