# How to add a custom notification provider

This guide shows you how to integrate a new notification service.

## 1) Create the provider module

Create a folder in `src/moodlemate/providers/notification/` and add `__init__.py`
plus `provider.py`.

Example file: `src/moodlemate/providers/notification/my_service/provider.py`

```python
import logging

from moodlemate.infrastructure.http.request_manager import request_manager
from moodlemate.notifications.base import NotificationProvider

logger = logging.getLogger(__name__)


class MyServiceProvider(NotificationProvider):
    def __init__(self, api_key: str, endpoint: str = "https://api.myservice.com"):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = request_manager.session

    def send(self, subject: str, message: str, summary: str | None = None) -> bool:
        payload = {"title": subject, "body": message}
        if summary:
            payload["summary"] = summary

        request_manager.update_headers(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        try:
            response = self.session.post(f"{self.endpoint}/send", json=payload)
        except Exception as exc:
            logger.error("MyService send failed: %s", exc)
            return False

        if 200 <= response.status_code < 300:
            return True

        logger.error("MyService error: %s - %s", response.status_code, response.text)
        return False
```

## 2) Add a config model

In `src/moodlemate/config.py`, add a config model:

```python
class MyServiceConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    endpoint: str = "https://api.myservice.com"
```

## 3) Register it in `Settings`

Still in `src/moodlemate/config.py`, add a field that matches the folder name:

```python
class Settings(BaseSettings):
    # Providers
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    webhook_site: WebhookSiteConfig = Field(default_factory=WebhookSiteConfig)
    pushbullet: PushbulletConfig = Field(default_factory=PushbulletConfig)
    my_service: MyServiceConfig = Field(default_factory=MyServiceConfig)
```

## 4) Configure `.env`

Add the provider variables:

```env
MOODLEMATE_MY_SERVICE__ENABLED=true
MOODLEMATE_MY_SERVICE__API_KEY=secret_key_123
MOODLEMATE_MY_SERVICE__ENDPOINT=https://api.myservice.com
```

## 5) Send a test notification

```bash
uv run moodlemate --test-notification
```
