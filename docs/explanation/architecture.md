# Architecture overview

Moodle Mate is structured as a pipeline that pulls Moodle notifications,
processes them, and fan-outs to providers.

## Core flow

1. `moodlemate.moodle.api.MoodleAPI` handles login and Moodle API calls.
2. `moodlemate.moodle.notification_handler.MoodleNotificationHandler` fetches
   new notifications and marks them processed.
3. `moodlemate.notifications.processor.NotificationProcessor` sanitizes content,
   applies filters, optionally summarizes, and dispatches to providers.
4. Providers in `moodlemate.providers.notification.*` send outbound messages.
5. `moodlemate.core.state_manager.StateManager` tracks last notification ID and
   keeps a small history for the Web UI.

## Why this structure

- Separation keeps Moodle-specific concerns isolated from notification delivery.
- Providers are modular, so adding a new destination does not change the core
  pipeline.
- The `src/` layout prevents accidental imports from the repo root and makes
  packaging predictable.
