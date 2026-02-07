# Moodle Mate Release Runbook (Agent-Ready)

This file is the source of truth for how to make changes and release safely.

## 1. Branch Strategy

1. Do feature work on `dev` (or short-lived `feat/*` branches merged into `dev`).
2. Keep `main` as release/stable.
3. Promote to release by merging `dev` into `main` (prefer fast-forward when possible).
4. Never delete `dev`.
5. After hotfixes on `main`, sync `dev` from `main`.

## 2. Commit Rules (Required for Auto Versioning)

Use Conventional Commits:

1. `fix:` -> patch bump
2. `feat:` -> minor bump
3. `type!:` or `BREAKING CHANGE:` -> major bump
4. `docs:`, `chore:`, `test:` usually do not trigger a release

Examples:

1. `fix(web): sanitize config error responses`
2. `feat(notification): add gotify provider`
3. `feat(api)!: remove legacy auth endpoint`

## 3. Release Automation in This Repo

Configured files:

1. `.github/workflows/release-please.yml`
2. `.github/release-please/config.json`
3. `.github/release-please/manifest.json`
4. `CHANGELOG.md`

Release Please updates:

1. `pyproject.toml`
2. `src/moodlemate/core/version.py`
3. `.github/release-please/manifest.json`
4. `CHANGELOG.md`

## 4. One-Time GitHub Setting Check

In GitHub repository settings:

1. `Settings -> Actions -> General -> Workflow permissions`
2. Set `Read and write permissions`
3. Enable `Allow GitHub Actions to create and approve pull requests`

Without this, Release Please cannot open release PRs.

## 5. Change Workflow (Daily)

1. `git checkout dev`
2. Make changes.
3. Run checks:
   1. `uv run ruff check --output-format=concise .`
   2. `uv run ruff format --check .`
   3. `uv run pytest -q`
4. Commit with Conventional Commit message.
5. `git push origin dev`
6. Merge `dev` -> `main` when ready for release.

## 6. Release Workflow (Agent Execution)

### A) Prepare `main`

1. `git checkout main`
2. `git pull --ff-only origin main`
3. Ensure clean tree: `git status`
4. Run checks:
   1. `uv run ruff check --output-format=concise .`
   2. `uv run ruff format --check .`
   3. `uv run pytest -q`

### B) Trigger Release Please

1. Push releasable commits to `main` (`fix:` or `feat:` etc.).
2. Release Please runs automatically on push to `main`.
3. It should open/update a release PR.

### C) Merge Release PR

1. Review release PR contents (version files + changelog).
2. Merge release PR.
3. Verify new tag and GitHub Release were created.

### D) Sync Back

1. `git checkout dev`
2. `git pull --ff-only origin dev`
3. `git merge --ff-only origin/main`
4. `git push origin dev`

## 7. Verification Commands

Use these after triggering release:

1. Workflow runs:
   1. `curl -s "https://api.github.com/repos/EvickaStudio/Moodle-Mate/actions/workflows/release-please.yml/runs?per_page=5" | jq -r '.workflow_runs[] | "run=\(.id) status=\(.status) conclusion=\(.conclusion) head=\(.head_sha[0:7]) created=\(.created_at)"'`
2. Open release PR:
   1. `curl -s "https://api.github.com/repos/EvickaStudio/Moodle-Mate/pulls?state=open&per_page=100" | jq -r '.[] | select(.head.ref|startswith("release-please--")) | "#\(.number) | \(.title) | head=\(.head.ref)"'`
3. Tags:
   1. `curl -s "https://api.github.com/repos/EvickaStudio/Moodle-Mate/tags?per_page=20" | jq -r '.[].name'`
4. Releases:
   1. `curl -s "https://api.github.com/repos/EvickaStudio/Moodle-Mate/releases?per_page=20" | jq -r '.[] | "\(.tag_name) | \(.name // "") | draft=\(.draft) prerelease=\(.prerelease)"'`

## 8. Troubleshooting

1. Error: `GitHub Actions is not permitted to create or approve pull requests`
   1. Fix GitHub Actions permissions (section 4).
2. No release PR created, workflow succeeded
   1. Usually no releasable commits on `main`.
   2. Add at least one `fix:` or `feat:` commit and push.
3. Old commit parse warnings in logs
   1. Non-Conventional old history causes warnings.
   2. Not fatal by itself if PR creation still works.
4. Stale release-please temporary branch exists
   1. Delete it:
   2. `git push origin --delete release-please--branches--main--components--moodle-mate`

## 9. Copy-Paste Prompt for an Agent

Use this exact prompt with an agent:

```text
Act as Release Operator for this repository.

Rules:
- Do not delete the dev branch.
- Use Conventional Commits only.
- Do not use destructive git commands.
- Run full checks before pushing.

Tasks:
1) Ensure local branch is main and clean.
2) Run:
   - uv run ruff check --output-format=concise .
   - uv run ruff format --check .
   - uv run pytest -q
3) If no releasable commit exists on main, create a minimal safe `fix:` commit.
4) Push main.
5) Verify release-please workflow run succeeded.
6) Verify release PR exists (or explain why not).
7) After release PR is merged, verify new tag + GitHub Release exist.
8) Merge origin/main back into dev and push dev.
9) Return a final report with:
   - workflow run id + status
   - release PR number/title
   - created tag
   - created release
   - final origin/main and origin/dev commit SHAs
```
