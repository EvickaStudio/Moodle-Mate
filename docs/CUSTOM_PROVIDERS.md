# Creating Custom Notification Providers

MoodleMate features a dynamic plugin system that allows you to create and integrate your own notification providers without altering the core application code. This makes it easy to extend MoodleMate to support any notification service with an API.

## How It Works

The application automatically discovers and loads any provider located in the `src/providers/notification/` directory. When you run the configuration generator (`--gen-config`), it will find your custom provider and interactively prompt you for the necessary configuration values.

## Steps to Create a Custom Provider

### 1. Create the Provider Directory and File

First, create a new directory for your provider inside `src/providers/notification/`. The directory name should be the desired name for your provider (e.g., `slack`, `ntfy`).

Inside this new directory, create a file named `provider.py`.

Your file structure should look like this:

```
src/
└── providers/
    └── notification/
        ├── your_provider_name/
        │   ├── __init__.py  (can be empty)
        │   └── provider.py
        └── ... (other providers)
```

### 2. Implement the Provider Class

Copy the template from `src/templates/notification_service_template.py` into your new `provider.py` file. This provides the basic structure for your provider.

Alternatively, you can create the class from scratch. It must inherit from `NotificationProvider` and implement the `send` method.

Here is a complete example for a hypothetical service called `MyPusher`:

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

**Key Points:**

- **Class Name:** The class name should be descriptive (e.g., `MyPusherProvider`).
- **`__init__` Method:** The parameters of your `__init__` method (excluding `self` and `kwargs`) directly define the configuration fields for your provider. The config generator (`python main.py --gen-config`) will automatically discover these parameters and interactively prompt the user for their values. Use type hints for clarity and default values for optional parameters.
- **`send` Method:** This is where you implement the core logic to send the notification. It receives the `subject` (string), `message` (string, always in Markdown format), and an optional `summary` (string, also in Markdown).
- **`provider_name` Attribute:** While not strictly required, it's good practice to set a `provider_name` class attribute (e.g., `provider_name: str = "MyPusher"`). This name is used internally for logging and identification.
- **`request_manager`:** For making HTTP requests, it's highly recommended to use the global `request_manager.session` (from `src.infrastructure.http.request_manager`) to benefit from consistent headers, session management, and connection pooling.

### 3. Generate the Configuration

Run the interactive configuration generator:

```bash
python main.py --gen-config
```

The generator will automatically detect your new `MyPusher` provider and prompt you to enable and configure it. It will ask for the `api_token` and `user_key` as defined in your `__init__` method.

After you complete the process, your `config.ini` will have a new section:

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
