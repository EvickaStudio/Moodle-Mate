---
icon: material/puzzle-plus
description: Add a custom notification provider to Moodle Mate using the plugin loader.
---

# How to add a custom notification provider

Moodle Mate auto-discovers providers by scanning
`src/moodlemate/providers/notification/*/provider.py`.
This guide walks through the minimal, code-accurate path for adding your own.

## How provider loading works

A provider is loaded when **all** of the following are true:

1. It lives at `src/moodlemate/providers/notification/<name>/provider.py`.
2. It defines a class that subclasses `NotificationProvider`.
3. `Settings` has a field named exactly `<name>` (matching the folder name).
4. `<name>.enabled` is `true` in configuration.

The plugin manager initialises each provider with:

```python
provider_settings.model_dump(exclude={"enabled"})
```

So your `__init__` parameters must match your config model fields **except** `enabled`.

## 1 — Create the provider module

Create two files:

```text
src/moodlemate/providers/notification/my_service/__init__.py  # empty
src/moodlemate/providers/notification/my_service/provider.py
```

Minimal `provider.py`:

```python title="provider.py"
import logging

from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)


class MyServiceProvider(NotificationProvider):
    def __init__(self, api_key: str, endpoint: str = "https://api.myservice.com"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = request_manager.get_session("provider_my_service")  # (1)!

    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        payload = {"title": subject, "body": message}
        if summary:
            payload["summary"] = summary

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self.session.post(
                f"{self.endpoint}/send",
                json=payload,
                headers=headers,
            )
        except Exception as exc:
            logger.error("MyService send failed: %s", exc)
            return False

        if 200 <= response.status_code < 300:
            return True

        logger.error("MyService error: %s - %s", response.status_code, response.text)
        return False
```

1.  Use `request_manager.get_session` with a unique name so your provider participates
    in the shared retry/timeout configuration set at startup.

## 2 — Add a config model in `src/moodlemate/config.py`

```python title="config.py (add near the other provider config classes)"
from pydantic import BaseModel


class MyServiceConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    endpoint: str = "https://api.myservice.com"
```

## 3 — Register the model in `Settings`

```python title="config.py (inside the Settings class)"
class Settings(BaseSettings):
    # ... existing fields ...
    my_service: MyServiceConfig = Field(default_factory=MyServiceConfig)  # (1)!
```

1.  The field name `my_service` must match the provider folder name exactly.
    The env prefix becomes `MOODLEMATE_MY_SERVICE__*`.

## 4 — Configure `.env`

```env title=".env"
MOODLEMATE_MY_SERVICE__ENABLED=true
MOODLEMATE_MY_SERVICE__API_KEY=secret_key_123
MOODLEMATE_MY_SERVICE__ENDPOINT=https://api.myservice.com
```

## 5 — Test

```bash
uv run moodlemate --test-notification
```

## Troubleshooting

??? question "Provider not loaded at all"
    Check all three conditions are met:

    - Folder name matches the `Settings` field name exactly.
    - Provider class subclasses `NotificationProvider`.
    - `MOODLEMATE_<NAME>__ENABLED=true` is set in `.env`.

??? question "Provider constructor error on startup"
    Ensure your `__init__` parameters match the config model fields **excluding** `enabled`.
    The plugin manager calls `model_dump(exclude={"enabled"})` and passes the result as kwargs.

??? question "Provider sends but message is empty"
    Check that `subject`, `message`, and optionally `summary` are what you expect.
    Add a `logger.debug(...)` to your `send()` method and re-run to inspect.

??? question "No log output from my provider at all"
    Make sure your module imports succeed (check for typos in the import path).
    Run `uv run moodlemate` (without `--test-notification`) and watch startup logs.

## Related

- Reference: [Configuration](../reference/configuration.md)
- Reference: [CLI](../reference/cli.md)
