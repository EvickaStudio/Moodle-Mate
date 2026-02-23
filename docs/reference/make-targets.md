# Make Targets Reference

Moodle Mate provides a `Makefile` for common workflows.

## Discovery

List all available targets:

```bash
make help
```

## Common targets

| Target | Purpose |
| --- | --- |
| `make install` | Install runtime dependencies (`uv sync`) |
| `make install-dev` | Install runtime + dev dependencies |
| `make run` | Run app via entrypoint (`uv run moodlemate`) |
| `make run-module` | Run app as module (`uv run python -m moodlemate`) |
| `make test` | Run pytest |
| `make test-cov` | Run tests with coverage |
| `make check` | Run formatter + lint autofix |
| `make ci-local` | Run CI-like local checks |
| `make typecheck` | Run pyright |
| `make test-notification` | Send test notification with current `.env` |

## Dependency and lockfile targets

| Target | Purpose |
| --- | --- |
| `make lock` | Refresh `uv.lock` |
| `make lock-upgrade` | Upgrade dependencies and refresh lock |
| `make export-requirements-runtime` | Export `requirements.txt` |
| `make export-requirements-dev` | Export `requirements-dev.txt` |
| `make sync` | Refresh lock + requirements files |
| `make sync-dev` | Upgrade lock, sync dev deps, refresh requirements |
| `make refresh` | `sync` + `check` |

## Docker targets

| Target | Purpose |
| --- | --- |
| `make docker-build` | Build Docker image |
| `make docker-up` | Start Docker stack in background |
| `make docker-down` | Stop Docker stack |
| `make docker-logs` | Follow Docker logs |
| `make docker-restart` | Restart Docker stack |

## Suggested usage patterns

### Daily development

```bash
make run
make test
make check
```

### Before committing

```bash
make ci-local
```

### Dependency refresh

```bash
make sync-dev
```

## Related

- How-to: [Prepare changes before committing](../how-to/prepare-commit.md)
