# Notification Service Modules

## Overview
This directory contains modular notification service modules, allowing for easy integration and extension with various notification platforms. Currently implemented modules are for Discord, Ntfy, and Pushbullet. The structure is designed to accommodate additional notification services in the future.

### Modules
- [Discord](#discord)
- [Ntfy](#ntfy)
- [Pushbullet](#pushbullet)

## [Discord](discord.py)
The `Discord` module allows for sending notifications to a Discord channel via webhooks. It supports rich embeds and formatting for detailed messages.

### Usage
To use the Discord module:
1. Initialize the `Discord` class with your webhook URL.
2. Use the `send_notification` method to send your message.

Example:
```python
from discord import Discord

discord_notifier = Discord("<webhook_url>")
discord_notifier.send_notification("Subject", "Message", "Summary", "Full Name", "<picture_url>")
```

## [Ntfy](ntfy.py)
The `Ntfy` module facilitates sending simple notifications to an Ntfy server. This can be useful for quick and straightforward alerts. A Ntfy server can be easily self-hosted :D.

### Usage
To use the Ntfy module:
1. Initialize the `Ntfy` class.
2. Set the server URL and topic.
3. Use the `send_notification` method to send your notification.

Example:
```python
from ntfy import Ntfy

ntfy_notifier = Ntfy()
ntfy_notifier.server_url = "<server_url>"
ntfy_notifier.send_notification("topic", "Title", "Message", "Priority")
```

## [Pushbullet](pushbullet.py)
The `Pushbullet` module enables sending push notifications to devices using the Pushbullet service. It's suitable for personal or group notifications.

### Usage
To use the Pushbullet module:
1. Initialize the `Pushbullet` class with your API key.
2. Use the `send_notification` method to send your notification.

Example:
```python
from notification.pushbullet import Pushbullet

pushbullet_notifier = Pushbullet("<api_key>")
pushbullet_notifier.send_notification("Title", "Body of the message")
```

## Extending the Notification Services
To add a new notification service:
1. Create a new module in this directory.
2. Implement a class with a standardized interface, similar to the existing modules.
3. Ensure that your class has methods for initialization and sending notifications.
4. Import your module in the main function and send your notifications.
5. Have luck and it should work!