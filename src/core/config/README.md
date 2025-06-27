# Configuration

The `config.ini` file controls all aspects of Moodle Mate. You can generate this file by running `python main.py --gen-config`.

## Core Sections

### Moodle Settings

This section contains your Moodle instance credentials.

```ini
[moodle]
url = https://your.moodle.instance
username = your_username
password = your_password
```

### AI Settings

This section controls the optional AI-powered summarization feature.

```ini
[ai]
enabled = 1
api_key = your_api_key
model = gpt-4o-mini
# Or models from eg. openrouter:
# model = google/gemini-flash-1.5
temperature = 0.7
max_tokens = 150
system_prompt = Summarize the message concisely with appropriate emojis, excluding links.
endpoint = https://api.openai.com/v1/
# For a custom endpoint like OpenRouter, you can use:
# endpoint = https://openrouter.ai/api/v1/
```

### Notification Settings

General settings for notification fetching and retries.

```ini
[notification]
max_retries = 5
fetch_interval = 60  ; in seconds
```

## Notification Provider Settings

MoodleMate uses a plugin system for notification providers. Any provider you create or have in the `src/providers/notification` directory will be discovered by the config generator.

For each provider, a section will be created in `config.ini`. The fields in each section are based on the parameters of the provider's `__init__` method.

Here are examples for the built-in providers:

### Discord

```ini
[discord]
enabled = 1
webhook_url = your_discord_webhook_url
bot_name = MoodleMate
thumbnail_url =   ; Optional: URL for a thumbnail image in the embed
```

### Pushbullet

```ini
[pushbullet]
enabled = 0
api_key = your_pushbullet_api_key
include_summary = 1
```

### Webhook.site (for testing)

```ini
[webhook_site]
enabled = 0
webhook_url = your_webhook_site_url
include_summary = 1
```

To add a custom provider, see the [Creating Custom Notification Providers](../docs/CUSTOM_PROVIDERS.md) guide.