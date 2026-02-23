# How to prepare changes before committing

Use this guide before opening a PR or pushing a feature branch.

## Scope

This page covers contributor checks only.

!!! note

    Release promotion steps are intentionally not documented here. Release operations are owner-only.

## Recommended pre-commit flow

1. Ensure dependencies are up to date for local development:

   ```bash
   make install-dev
   ```

2. Run local quality checks:

   ```bash
   make check
   make test
   ```

3. Run CI-aligned checks:

   ```bash
   make ci-local
   ```

4. Confirm no unexpected files changed:

   ```bash
   git status
   ```

5. Commit with a Conventional Commit message:

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

## What each check catches

- `make check`:
  - `ruff format` (formatting)
  - `ruff check --fix` (lint + safe autofixes)
- `make test`:
  - pytest suite
- `make ci-local`:
  - non-mutating lint/format checks + tests, matching CI behavior

## Related

- Reference: [Make targets](../reference/make-targets.md)
- How-to: [Set up development environment](setup-dev-environment.md)
