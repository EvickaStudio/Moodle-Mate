# Moodle-Mate Configuration Guide

This document provides a comprehensive guide to configuring Moodle-Mate using the `config.ini` file. You can generate an interactive configuration by running `python main.py --gen-config`.

---

## Core Sections

### Moodle Settings (`[moodle]`)

This section contains your Moodle instance credentials and settings related to fetching notifications.

- `url`: The base URL of your Moodle instance (e.g., `https://your.moodle.instance`).
- `username`: Your Moodle username.
- `password`: Your Moodle password.
- `initial_fetch_count`: (Optional) On the very first run (when no `state.json` exists), this specifies how many of the most recent notifications to fetch and process. Defaults to `1`.

```ini
[moodle]
url = https://your.moodle.instance
username = your_username
password = your_password
initial_fetch_count = 5
```

### AI Settings (`[ai]`)

This section controls the optional AI-powered summarization feature for notifications.

- `enabled`: Set to `1` to enable AI summarization, `0` to disable.
- `api_key`: Your API key for the chosen AI provider (e.g., OpenAI API key).
- `model`: The name of the AI model to use (e.g., `gpt-4o-mini`, `google/gemini-flash-1.5`).
- `temperature`: Controls the randomness of the AI's output. Lower values (e.g., `0.0`) make it more deterministic, higher values (e.g., `1.0`) make it more creative
- `max_tokens`: The maximum number of tokens the AI should generate in its summary.  
  *Note: A token is a unit used by language models and may represent a word, part of a word, or even punctuation. The number of tokens is not the same as the number of words or characters.*
- `system_prompt`: A prompt that guides the AI's behavior and style for summarization.
- `endpoint`: (Optional) A custom API endpoint URL for AI services (e.g., for self-hosted models or services like OpenRouter). If not set, it defaults to OpenAI's endpoint.

```ini
[ai]
enabled = 1
api_key = your_api_key
model = gpt-4o-mini
temperature = 0.7
max_tokens = 150
system_prompt = Summarize the message concisely with appropriate emojis, excluding links.
endpoint = https://api.openai.com/v1/
# For a custom endpoint like OpenRouter, you can use:
# endpoint = https://openrouter.ai/api/v1/
```

### Notification Settings (`[notification]`)

General settings for how Moodle-Mate fetches and retries notification processing.

- `max_retries`: The maximum number of times Moodle-Mate will retry fetching notifications if an error occurs.
- `fetch_interval`: The interval (in seconds) between attempts to fetch new notifications from Moodle.

```ini
[notification]
max_retries = 5
fetch_interval = 60
```

### Notification Filters (`[filters]`)

This section allows you to define rules to ignore certain notifications based on their content.

- `ignore_subjects_containing`: (Optional) A comma-separated list of phrases. Notifications with subjects containing any of these phrases will be ignored. (e.g., `forum digest, test`).
- `ignore_courses_by_id`: (Optional) A comma-separated list of Moodle course IDs. Notifications originating from these courses will be ignored. (e.g., `123, 456`). *Note: This feature is currently a placeholder and requires further Moodle API integration to function.*

```ini
[filters]
ignore_subjects_containing = forum digest, course update
ignore_courses_by_id = 123, 456
```

### Health & Status Notifications (`[health]`)

This section configures Moodle-Mate to send periodic health reports and critical error alerts.

- `enabled`: Set to `1` to enable health notifications, `0` to disable.
- `heartbeat_interval`: (Optional) The interval (in hours) at which a "heartbeat" notification will be sent to confirm Moodle-Mate is running. If not set, heartbeat notifications are disabled.
- `failure_alert_threshold`: (Optional) The number of consecutive errors after which a "failure alert" notification will be sent. If not set, failure alerts are disabled.
- `target_provider`: (Optional) The name of the notification provider (e.g., `discord`, `pushbullet`) to which health and status notifications should be sent. This provider must also be enabled in its respective section.

```ini
[health]
enabled = 1
heartbeat_interval = 24
failure_alert_threshold = 5
target_provider = discord
```

---

## Notification Provider Settings

Moodle-Mate uses a plugin system for notification providers. Any provider you create or have in the `src/providers/notification` directory will be discovered by the config generator.

For each provider, a section will be created in `config.ini`. The fields in each section are based on the parameters of the provider's `__init__` method.

### Common Provider Options

All provider sections will have an `enabled` option:

- `enabled`: Set to `1` to enable this notification provider, `0` to disable.

### Discord (`[discord]`)

- `webhook_url`: The Discord webhook URL where notifications will be sent.
- `bot_name`: The name that will appear as the sender of the Discord messages.
- `thumbnail_url`: (Optional) A URL for a thumbnail image to be displayed in the Discord embed.

```ini
[discord]
enabled = 1
webhook_url = your_discord_webhook_url
bot_name = MoodleMate
thumbnail_url =
```

### Pushbullet (`[pushbullet]`)

- `api_key`: Your Pushbullet API key.
- `include_summary`: Set to `1` to include the AI-generated summary in Pushbullet notifications, `0` to exclude it.

```ini
[pushbullet]
enabled = 0
api_key = your_pushbullet_api_key
include_summary = 1
```

### Webhook.site (`[webhook_site]`)

This provider is primarily for testing and debugging purposes.

- `webhook_url`: The Webhook.site URL to which notifications will be sent.
- `include_summary`: Set to `1` to include the AI-generated summary as a separate field in the webhook payload, `0` to exclude it.

```ini
[webhook_site]
enabled = 0
webhook_url = https://webhook.site/your-unique-id
include_summary = 1
```

### Custom Providers (`[your_custom_provider_name]`)

If you create a custom notification provider, its configuration section will be dynamically generated based on the parameters defined in its `__init__` method.

```ini
[your_custom_provider_name]
enabled = 1
# ... other parameters as defined in your provider's __init__ method
api_token = your_secret_token
custom_setting = some_value
```
