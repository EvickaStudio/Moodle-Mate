---
title: Moodle Mate Documentation
icon: material/school
description: Documentation for Moodle Mate, the smart Moodle notification assistant.
---

# Moodle Mate Documentation

Moodle Mate polls your Moodle instance for new notifications and delivers them to your preferred
channels — Discord, Pushbullet, custom providers — with optional AI summaries and a local Web UI.

[Open GitHub Repository](https://github.com/EvickaStudio/Moodle-Mate){ .md-button .md-button--primary }
[Read the first tutorial](tutorials/first-notification.md){ .md-button }

## Quick start

```bash
# 1. Install dependencies
uv sync --extra dev

# 2. Create and edit your config
cp example.env .env

# 3. Verify a test notification is sent
uv run moodlemate --test-notification
```

!!! tip "Need `uv`?"
    Install it from [astral.sh/uv](https://astral.sh/uv) — `curl -LsSf https://astral.sh/uv/install.sh | sh`.

## Documentation map

<div class="grid cards" markdown>

-   :material-send-check: __Tutorials__

    ---

    Learn Moodle Mate by following hands-on, end-to-end tasks.

    [:octicons-arrow-right-24: Start here](tutorials/first-notification.md)

-   :material-wrench: __How-to guides__

    ---

    Complete specific tasks like configuring the Web UI or adding providers.

    [:octicons-arrow-right-24: Browse guides](how-to/index.md)

-   :material-book-open-page-variant: __Reference__

    ---

    Look up exact settings, environment variables, and CLI options.

    [:octicons-arrow-right-24: Open reference](reference/configuration.md)

-   :material-lightbulb-on-outline: __Explanation__

    ---

    Understand the architecture and security trade-offs.

    [:octicons-arrow-right-24: Explore concepts](explanation/architecture.md)

</div>

## Key facts

- Configuration is loaded from `.env` and environment variables prefixed with `MOODLEMATE_`.
- The Web UI binds to `127.0.0.1` by default and requires `MOODLEMATE_WEB__AUTH_SECRET` when enabled.
- For contributors, run `make check` and `make test` before every PR.
