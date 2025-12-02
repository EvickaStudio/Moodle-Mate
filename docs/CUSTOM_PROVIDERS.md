# Creating Custom Notification Providers

Moodle-Mate uses a modular provider system. Adding a new notification service requires three steps: creating the provider class, defining its configuration, and enabling it in the settings.

## Quick Overview

1. **Create Provider**: Add `src/providers/notification/<name>/provider.py`.
2. **Define Config**: Add a Pydantic model to `src/config.py`.
3. **Register**: Add the config field to the `Settings` class in `src/config.py`.
4. **Configure**: Set environment variables in `.env`.

## Step-by-Step Guide

### 1. Create the Provider

Create a directory in `src/providers/notification/` with your provider name (e.g., `my_service`). inside, create an empty `__init__.py` and a `provider.py`.

**File:** `src/providers/notification/my_service/provider.py`

```python
import logging
from typing import Optional
from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)

class MyServiceProvider(NotificationProvider):
    """My Custom Notification Service."""

    def __init__(self, api_key: str, endpoint: str = "https://api.myservice.com"):
        """
        Initialize with values from Settings.
        Args match the fields in your Config model.
        """
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.session = request_manager.session

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        try:
            # Prepare payload
            payload = {
                "title": subject,
                "body": message
            }
            if summary:
                payload["summary"] = summary

            # Set headers
            request_manager.update_headers({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })

            # Send request
            response = self.session.post(f"{self.endpoint}/send", json=payload)
            
            if 200 <= response.status_code < 300:
                logger.info("Notification sent successfully to MyService")
                return True
            
            logger.error(f"MyService error: {response.status_code} - {response.text}")
            return False

        except Exception as e:
            logger.error(f"Failed to send to MyService: {e}")
            return False
```

### 2. Define Configuration

Open `src/config.py` and add a configuration model for your service.

```python
# src/config.py

# ... existing imports ...

# ... existing config classes ...

class MyServiceConfig(BaseModel):
    enabled: bool = False
    api_key: str = ""
    endpoint: str = "https://api.myservice.com"
```

### 3. Register in Settings

In the same `src/config.py` file, find the `Settings` class and add your new config as a field. The field name **must match** the directory name you created in Step 1.

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # Providers
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    webhook_site: WebhookSiteConfig = Field(default_factory=WebhookSiteConfig)
    pushbullet: PushbulletConfig = Field(default_factory=PushbulletConfig)
    
    # Add your new provider here:
    my_service: MyServiceConfig = Field(default_factory=MyServiceConfig)
```

### 4. Configure Environment Variables

Add your settings to your `.env` file. The prefix is `MOODLEMATE_` followed by your provider name (uppercase) and field name (uppercase), separated by double underscores.

```env
MOODLEMATE_MY_SERVICE__ENABLED=true
MOODLEMATE_MY_SERVICE__API_KEY=secret_key_123
# MOODLEMATE_MY_SERVICE__ENDPOINT=https://custom.endpoint.com
```

### 5. Test It

Run the test command to verify your new provider works:

```bash
python main.py --test-notification
```

## Best Practices

- **Type Safety**: Use appropriate types in your Pydantic model (`int`, `str`, `Optional`).
- **Validation**: Pydantic handles basic validation. Add `validator` decorators in your config model if you need complex checks.
- **HTTP Client**: Always use `request_manager.session` to benefit from global connection pooling and timeouts.
- **Logging**: Log errors clearly but **never log API keys or secrets**.
