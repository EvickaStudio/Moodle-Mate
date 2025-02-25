# Creating a Custom Notification Provider for MoodleMate

This guide will walk you through the process of creating your own notification provider for MoodleMate. By following these steps, you can extend the application to send notifications through any service you need.

## Overview

Creating a custom notification provider involves:

1. Creating the provider implementation
2. Updating the configuration schema
3. Updating the configuration loader
4. Registering the provider in the initialization system

## Step 1: Create the Provider Implementation

First, create a directory structure for your provider:

```
src/providers/notification/your_service_name/
└── provider.py
```

Implement your provider by extending the `NotificationProvider` base class:

```python:src/providers/notification/your_service_name/provider.py
import logging
from typing import Optional

from src.core.notification.base import NotificationProvider
from src.infrastructure.http.request_manager import request_manager

logger = logging.getLogger(__name__)


class YourServiceNameProvider(NotificationProvider):
    """Your service description here."""

    def __init__(self, api_key: str, some_option: str = "default", **kwargs) -> None:
        """Initialize your provider.

        Args:
            api_key: API key for authentication
            some_option: Some configuration option
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.some_option = some_option
        self.session = request_manager.session

    def send(self, subject: str, message: str, summary: Optional[str] = None) -> bool:
        """Send a notification through your service.

        Args:
            subject: Notification subject/title
            message: Main notification content
            summary: Optional summary text

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the payload for your service
            payload = {
                "title": subject,
                "body": message,
                "summary": summary if summary else "",
            }

            # Send the request to your service
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = self.session.post(
                "https://api.yourservice.com/send",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                logger.info("Successfully sent notification via YourServiceName")
                return True

            logger.error(
                "API returned unexpected status code: %d, Response: %s",
                response.status_code,
                response.text,
            )
            return False

        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
```

## Step 2: Update the Configuration Schema

Add a configuration class for your provider in `src/core/config/schema.py`:

```python:src/core/config/schema.py
@dataclass
class YourServiceNameConfig:
    """Configuration for your notification provider."""
    enabled: bool = False
    api_key: str = ""
    some_option: str = "default"
    # Add any other configuration options your provider needs
```

## Step 3: Update the Configuration Loader

Modify `src/core/config/loader.py` to load your provider's configuration:

1. Import your config class:

```python
from .schema import (
    AIConfig,
    DiscordConfig,
    MoodleConfig,
    NotificationConfig,
    ProviderConfig,
    WebhookSiteConfig,
    YourServiceNameConfig,  # Add your config class
)
```

2. Add a method to load your provider's configuration:

```python
def _load_your_service_name_config(self) -> YourServiceNameConfig:
    """Load your service configuration."""
    return YourServiceNameConfig(
        enabled=self._get_bool("your_service_name", "enabled", False),
        api_key=self._get_config("your_service_name", "api_key", ""),
        some_option=self._get_config("your_service_name", "some_option", "default"),
        # Add any other configuration options
    )
```

3. Update the `_init_config` method to call your loader:

```python
def _init_config(self, config_path: str):
    """Initialize configuration from file."""
    self.config = configparser.ConfigParser()
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    self.config.read(config_path)

    # Initialize config sections
    self.moodle = self._load_moodle_config()
    self.ai = self._load_ai_config()
    self.notification = self._load_notification_config()

    # Load built-in providers
    self.discord = self._load_discord_config()
    self.webhook_site = self._load_webhook_site_config()
    self.your_service_name = self._load_your_service_name_config()  # Add your provider

    # Load dynamic provider configurations
    self._load_provider_configs()
```

4. Update the `_load_provider_configs` method to exclude your provider:

```python
def _load_provider_configs(self):
    """Dynamically load configuration for all providers."""
    # Get all sections that might be providers
    for section in self.config.sections():
        # Skip known non-provider sections
        if section in [
            "moodle",
            "ai",
            "notification",
            "discord",
            "webhook_site",
            "your_service_name",  # Add your provider
        ]:
            continue
```

## Step 4: Register Your Provider in the Initialization System

Update `src/providers/notification/__init__.py` to import and initialize your provider:

1. Import your provider:

```python
from .discord.provider import DiscordProvider
from .webhook_site.provider import WebhookSiteProvider
from .your_service_name.provider import YourServiceNameProvider  # Add your provider
```

2. Update the `initialize_providers` function to initialize your provider:

```python
# Initialize your provider if enabled
if hasattr(config, "your_service_name") and config.your_service_name.enabled:
    logger.info("Initializing YourServiceName provider")
    providers.append(
        YourServiceNameProvider(
            api_key=config.your_service_name.api_key,
            some_option=config.your_service_name.some_option,
            # Add any other configuration options
        )
    )
    already_loaded_providers.add("your_service_name")
```

3. Update the `__all__` list to include your provider:

```python
__all__ = [
    "DiscordProvider",
    "WebhookSiteProvider",
    "YourServiceNameProvider",  # Add your provider
    "initialize_providers",
]
```

## Step 5: Add Configuration to config.ini

Add a section for your provider in `config.ini`:

```ini
[your_service_name]
enabled = 1
api_key = your_api_key_here
some_option = your_option_value
# Add any other configuration options
```
