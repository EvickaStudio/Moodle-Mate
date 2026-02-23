# How to add a custom notification provider

Moodle Mate auto-discovers providers from `src/moodlemate/providers/notification/*/provider.py`.

This guide shows the minimal, code-accurate integration path.

## How provider loading works

A provider is loaded when all of the following are true:

1. It lives under `src/moodlemate/providers/notification/<provider_name>/provider.py`.
2. It defines a class that subclasses `NotificationProvider`.
3. `Settings` contains a field named exactly `<provider_name>`.
4. `<provider_name>.enabled` is `true` in config.

The plugin manager initializes providers with:

- `provider_settings.model_dump(exclude={"enabled"})`

So your provider `__init__` parameters must match your config model fields except `enabled`.

## 1) Create provider module

Create:

```text
src/moodlemate/providers/notification/my_service/__init__.py
src/moodlemate/providers/notification/my_service/provider.py
```

Example `provider.py`:

```python
import logging

from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)


class MyServiceProvider(NotificationProvider):
    def __init__(self, api_key: str, endpoint: str = "https://api.myservice.com"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = request_manager.get_session("provider_my_service")

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

## 2) Add config model in `src/moodlemate/config.py`

```python
from pydantic import BaseModel, Field


class MyServiceConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    endpoint: str = "https://api.myservice.com"
```

## 3) Register the model in `Settings`

```python
class Settings(BaseSettings):
    # ...existing fields...
    my_service: MyServiceConfig = Field(default_factory=MyServiceConfig)
```

The field name `my_service` must match the provider folder name.

## 4) Configure `.env`

```env
MOODLEMATE_MY_SERVICE__ENABLED=true
MOODLEMATE_MY_SERVICE__API_KEY=secret_key_123
MOODLEMATE_MY_SERVICE__ENDPOINT=https://api.myservice.com
```

## 5) Test

```bash
uv run moodlemate --test-notification
```

## Troubleshooting

- Provider not loaded: check folder name, class inheritance, and `Settings` field name match.
- Provider constructor error: ensure `__init__` args match config model fields except `enabled`.
- No message delivered: check logs for your provider’s HTTP response status/body.

## Related

- Reference: [Configuration](../reference/configuration.md)
- Reference: [CLI](../reference/cli.md)
