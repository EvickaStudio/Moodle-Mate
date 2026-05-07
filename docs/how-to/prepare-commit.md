---
icon: material/check-decagram
description: Run the right checks and apply commit conventions before pushing your changes.
---

# How to prepare changes before committing

Use this guide before opening a PR or pushing a feature branch.

!!! note "Scope: contributor checks only"
    Release promotion steps are intentionally not documented here. Release operations are owner-only.

## Recommended pre-commit flow

1.  Ensure dev dependencies are up to date:

    ```bash
    make install-dev
    ```

2.  Run local quality checks:

    ```bash
    make check    # ruff format + ruff lint --fix (mutating)
    make test     # pytest
    ```

3.  Run CI-aligned checks (non-mutating — exactly what CI runs):

    ```bash
    make ci-local  # = ci-lint + ci-test
    ```

4.  Confirm no unexpected files changed:

    ```bash
    git status
    ```

5.  Commit with a [Conventional Commit](https://www.conventionalcommits.org/) message:

    ```text
    fix(web): prevent unsafe config updates from Web UI
    feat(provider): add example custom notification provider docs
    docs(mkdocs): add make command reference and commit checklist
    ```

## Fast command reference

=== "Everyday"

    ```bash
    make run
    make test
    make check
    ```

=== "Before commit"

    ```bash
    make ci-local
    ```

=== "When dependencies changed"

    ```bash
    make sync
    ```

## What each check does

| Command | What it catches |
|---------|----------------|
| `make format` | Runs `ruff format` and rewrites files in place |
| `make lint` | Runs `ruff check --fix` and applies safe auto-fixes |
| `make check` | Runs `format` + `lint` (both mutating) |
| `make format-check` | Checks formatting without modifying files (used in CI) |
| `make lint-check` | Lints without auto-fixes (used in CI) |
| `make ci-lint` | `format-check` + `lint-check` — non-mutating, matches CI |
| `make ci-test` | Runs pytest with quiet output — matches CI |
| `make ci-local` | `ci-lint` + `ci-test` — the full CI suite locally |
| `make test` | Full pytest run |
| `make typecheck` | Runs Pyright static type analysis |

## Related

- Full list of all make targets: [Make targets reference](../reference/make-targets.md)
- How-to: [Set up development environment](setup-dev-environment.md)
