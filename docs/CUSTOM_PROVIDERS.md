# Creating Custom Notification Providers

Moodle-Mate has a simple, dynamic plugin system that lets you add new notification providers without touching core code. Place your provider under `src/providers/notification/`, implement a tiny interface, and the app will auto-discover, configure, and run it.

## Provider lifecycle at a glance

1) Discovery: any folder under `src/providers/notification/<name>/provider.py` is scanned and classes inheriting `NotificationProvider` are picked up by the plugin manager.
2) Config generation: running the config generator inspects your provider `__init__` signature and prompts for those fields. It then writes a `[<name>]` section to `config.ini`.
3) Loading: on startup, enabled providers are constructed with values from `config.ini` and passed into the `NotificationProcessor`, which calls `provider.send(...)` for each notification.

Notes and caveats:
- Only explicit constructor parameters are prompted by the generator. `**kwargs` is ignored during prompting. If you need a field to be prompted, declare it as a named argument with a sensible default when optional.
- Values for dynamically loaded providers are read as strings from `config.ini`. Convert and validate types you require in your constructor (e.g., `int(timeout)`).
- Use the global HTTP `request_manager.session` for connection pooling and consistent headers.

## Steps to create a provider

### 1) Create the provider directory and file

Create `src/providers/notification/<your_provider_name>/provider.py` and an empty `__init__.py` in the same folder.

Example layout:

```
src/
└── providers/
    └── notification/
        ├── your_provider_name/
        │   ├── __init__.py
        │   └── provider.py
        └── discord/
            └── provider.py
```

### 2) Implement the provider class

Option A: copy the template from `src/templates/notification_service_template.py` and adapt it (now includes validation, structured logging, and header usage examples).

Option B: implement from scratch. Your class must inherit from `NotificationProvider` and implement `send(self, subject: str, message: str, summary: Optional[str]) -> bool`.

Minimal webhook-style example (`mypusher`):

```python
# src/providers/notification/mypusher/provider.py

import logging
from typing import Optional

from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class MyPusherProvider(NotificationProvider):
    """A custom provider for the MyPusher notification service."""

    def __init__(self, api_token: str, user_key: str):
        """Initializes the MyPusher provider.

        The parameters for this method (excluding `self`) will be used by the
        config generator to create the `config.ini` section for this provider.

        Args:
            api_token: The API token for authenticating with MyPusher.
            user_key: The user-specific key to send notifications to.
        """
        self.api_token = api_token
        self.user_key = user_key
        self.endpoint = "https://api.mypusher.net/v1/messages.json"
        self.session = request_manager.session

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        """Sends a notification using the MyPusher API."""
        try:
            payload = {
                "token": self.api_token,
                "user": self.user_key,
                "title": subject,
                "message": message,
            }

            if summary:
                payload["message"] += f"\n\n**Summary:**\n{summary}"

            headers = {"Content-Type": "application/json"}
            response = self.session.post(self.endpoint, json=payload, headers=headers)

            if response.status_code == 200:
                logger.info("Successfully sent MyPusher notification.")
                return True
            else:
                logger.error(
                    f"MyPusher API returned status {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to send MyPusher notification: {str(e)}")
            return False

```

**Key points:**

- **Class name:** Use a descriptive class name ending with `Provider` (e.g., `MyPusherProvider`).
- **Constructor drives config:** The `__init__` parameters (excluding `self` and `kwargs`) define which fields the generator will prompt for. Use defaults for optional fields. Remember that values are read as strings; convert/validate as needed.
- **`send` method:** Receives `subject` and Markdown `message`, plus optional Markdown `summary`. Return `True` on success, `False` otherwise.
- **`provider_name` attribute:** The plugin manager sets this automatically from the folder name; you can override for clarity.
- **Networking:** Use `request_manager.session` for HTTP calls and `request_manager.update_headers({...})` to add per-request headers.

### 3) Generate the configuration

Run the interactive configuration generator:

```bash
# standard Python
python main.py --gen-config
```

The generator will detect `mypusher` and prompt for `api_token` and `user_key` as defined in your constructor.

Afterwards, your `config.ini` will contain:

```ini
[mypusher]
enabled = 1
api_token = your_secret_api_token
user_key = your_secret_user_key
```

### 4. Run MoodleMate

That's it! When you start MoodleMate, it will load your custom provider and start sending notifications through it.

```bash
python main.py
```

### 5) Test your provider quickly

You can send a test notification to all enabled providers without connecting to Moodle:

```bash
python main.py --test-notification
```

## Troubleshooting and best practices

- Validate all required constructor params early and raise `ValueError` with a clear message.
- Convert types from strings (e.g., `timeout = int(timeout)`), and normalize URLs using `rstrip('/')` where appropriate.
- Log errors with context but never log secrets (API keys, tokens).
- Keep `send` focused: build payload → send request → check status → return `True/False`.
- Prefer small, explicit parameters over packing values into `**kwargs` so the config generator prompts users correctly.
