---
title: Moodle Mate Documentation
---

# Moodle Mate Documentation

Moodle Mate fetches Moodle notifications and delivers them to your preferred channels (Discord, Pushbullet, custom providers), with optional AI summaries and a local Web UI.

[Open GitHub Repository](https://github.com/EvickaStudio/Moodle-Mate){ .md-button .md-button--primary }
[Read the first tutorial](tutorials/first-notification.md){ .md-button }

## Quick start

```bash
uv sync --extra dev
cp example.env .env
uv run moodlemate --test-notification
```

## Documentation map

<div class="grid cards" markdown>

-   :material-school: __Tutorials__

    ---

    Learn Moodle Mate by doing practical, end-to-end tasks.

    [:octicons-arrow-right-24: Start here](tutorials/first-notification.md)

-   :material-wrench: __How-to guides__

    ---

    Complete specific tasks like configuring the Web UI or adding providers.

    [:octicons-arrow-right-24: Browse guides](how-to/setup-dev-environment.md)

-   :material-book-open-page-variant: __Reference__

    ---

    Look up exact settings, environment variables, and CLI options.

    [:octicons-arrow-right-24: Open reference](reference/configuration.md)

-   :material-lightbulb-on-outline: __Explanation__

    ---

    Understand architecture and security trade-offs.

    [:octicons-arrow-right-24: Explore concepts](explanation/architecture.md)

</div>

## Notes

- Configuration is loaded from `.env` and environment variables with `MOODLEMATE_` prefix.
- Web UI uses `127.0.0.1` by default and requires auth when enabled.
- For contributors, run checks before PRs: `make check` and `make test`.
