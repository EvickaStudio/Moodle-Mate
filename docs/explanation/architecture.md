# Architecture overview

Moodle Mate is a notification pipeline: fetch from Moodle, transform, optionally summarize, then fan out to providers.

## Runtime flow

1. `moodlemate.main` loads `Settings` and builds all runtime components.
2. `MoodleMateApp` starts optional Web UI and enters the polling loop.
3. `MoodleNotificationHandler` fetches notifications and determines unseen items.
4. `NotificationProcessor` sanitizes payloads, converts HTML to Markdown, applies filters, and optionally summarizes.
5. Enabled providers send notifications.
6. `StateManager` tracks last processed notification ID and keeps recent in-memory history for the Web UI.

## Provider architecture

Providers are discovered dynamically by package scanning under:

- `moodlemate.providers.notification.<name>.provider`

A provider is active only if:

- matching config exists in `Settings`
- `enabled=true`
- provider class subclasses `NotificationProvider`

## Reliability and control points

- Retry and timeout behavior comes from `notification.*` settings.
- Session refresh happens periodically in the main loop.
- State persistence is throttled and also forced on graceful shutdown.
- Health notifications can target a specific enabled provider.

## Design intent

- Clear separation: Moodle API, processing, delivery, and UI are decoupled.
- Extensibility: adding a provider does not require changing core dispatch logic.
- Operability: defensive retry, state persistence, and health routing support long-running deployment.

## Related

- [Security model](security.md)
- [Configuration reference](../reference/configuration.md)
