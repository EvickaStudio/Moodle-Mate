# Configuration

The `config.ini` file controls all aspects of Moodle Mate. Here are the key sections:

## Moodle Settings

```ini
[moodle]
url = https://your.moodle.instance
username = your_username
password = your_password
```

## AI Settings

```ini
[ai]
enabled = 1
api_key = your_api_key
model = gpt-4
temperature = 0.7 # The temperature and max_tokens have an default value
max_tokens = 150
system_prompt = Summarize the message concisely with appropriate emojis, excluding links. # An example system prompt that should be finetuned for your use case
endpoint = https://api.openai.com/v1  # Optional custom endpoint
```

## Notification Settings

```ini
[notification]
max_retries = 5 
fetch_interval = 60  # seconds
```

## Discord Settings

```ini
[discord]
enabled = 1
webhook_url = your_webhook_url
bot_name = MoodleMate
thumbnail_url = your_thumbnail_url # A optional thumbnail url for the webhook
```
