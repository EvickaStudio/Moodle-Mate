import logging
from typing import TYPE_CHECKING

from moodlemate.notifications.base import NotificationProvider
from moodlemate.providers.plugin_manager import PluginManager

from .discord.provider import DiscordProvider
from .pushbullet.provider import PushbulletProvider
from .webhook_site.provider import WebhookSiteProvider

if TYPE_CHECKING:
    from moodlemate.config import Settings

logger = logging.getLogger(__name__)


def initialize_providers(settings: "Settings") -> list[NotificationProvider]:
    """
    Initializes all enabled notification providers using the PluginManager.
    Args:
        settings: The application configuration.
    Returns:
        A list of initialized and enabled provider instances.
    """
    logger.info("Initializing notification providers...")
    enabled_providers = PluginManager.load_enabled_providers(settings)
    logger.info(
        f"Initialized {len(enabled_providers)} notification providers: {[p.__class__.__name__ for p in enabled_providers]}"
    )
    return enabled_providers


__all__ = [
    "DiscordProvider",
    "PushbulletProvider",
    "WebhookSiteProvider",
    "initialize_providers",
]
