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
4. To refresh to latest compatible dependencies for development:
   1. `make sync-dev`
   2. This runs: `uv lock --upgrade`, `uv sync --extra dev`, and regenerates `requirements.txt` + `requirements-dev.txt`.
5. Commit with Conventional Commit message.
6. `git push origin dev`
7. Merge `dev` -> `main` when ready for release.

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

### D) Sync Back (Required)

1. `git checkout dev`
2. `git pull --ff-only origin dev`
3. `git merge --ff-only origin/main`
4. `git push origin dev`
5. Verify both remote branches point to the same commit:
   1. `git fetch origin`
   2. `git rev-parse --short origin/main`
   3. `git rev-parse --short origin/dev`

### E) Keep `CHANGELOG.md` Conflict-Free

1. Do not edit `CHANGELOG.md` manually in regular feature commits.
2. Let Release Please own version files and changelog updates.
3. After each release PR merge, always run section **D) Sync Back (Required)** before starting new work.
4. If you also work locally on `main`, refresh it before switching back to `dev`:
   1. `git checkout main`
   2. `git pull --ff-only origin main`

## 7. Verification Commands

Use these after triggering release:

1. GitHub CLI auth:
   1. `gh auth status`
2. Workflow runs (Release Please):
   1. `gh run list --workflow release-please.yml --limit 5 --json databaseId,status,conclusion,headSha,createdAt,url --jq '.[] | "run=\(.databaseId) status=\(.status) conclusion=\(.conclusion) head=\(.headSha[0:7]) created=\(.createdAt) url=\(.url)"'`
3. Open release PR:
   1. `gh pr list --state open --search "head:release-please--branches--main--components--moodle-mate" --json number,title,headRefName,url --jq '.[] | "#\(.number) | \(.title) | head=\(.headRefName) | \(.url)"'`
4. Tags:
   1. `gh api "repos/EvickaStudio/Moodle-Mate/tags?per_page=20" --jq '.[].name'`
5. Releases:
   1. `gh api "repos/EvickaStudio/Moodle-Mate/releases?per_page=20" --jq '.[] | "\(.tag_name) | \(.name // "") | draft=\(.draft) prerelease=\(.prerelease)"'`

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

## 10. How to Get Better Release Notes

Release notes are generated from commit subjects. If commits are small or generic, notes look empty.

Do this:

1. Use meaningful Conventional Commit subjects:
   1. Good: `fix(web): block config updates for credential fields`
   2. Weak: `fix: update stuff`
2. Keep related changes grouped in one PR so release entries are coherent.
3. Prefer `feat:` and `fix:` for user-visible changes.
4. Use `docs:` for notable docs updates (now visible in changelog sections).
5. Add a short manual "Highlights" paragraph when publishing a major/minor release.
