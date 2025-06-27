import logging
from typing import List

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider
from src.core.plugin_manager import PluginManager

from .discord.provider import DiscordProvider
from .pushbullet.provider import PushbulletProvider
from .webhook_site.provider import WebhookSiteProvider

logger = logging.getLogger(__name__)


def initialize_providers(config: Config) -> List[NotificationProvider]:
    """
    Initializes all enabled notification providers using the PluginManager.
    This function relies on the PluginManager to discover all available providers,
    check if they are enabled in the configuration, and initialize them with their
    respective settings.
    Args:
        config: The application configuration.
    Returns:
        A list of initialized and enabled provider instances.
    """
    logger.info("Initializing notification providers...")
    enabled_providers = PluginManager.load_enabled_providers(config)
    logger.info(
        f"Initialized {len(enabled_providers)} notification providers: {[p.__class__.__name__ for p in enabled_providers]}"  # noqa: E501
    )
    loaded_provider_names = {p.provider_name for p in enabled_providers}
    configured_provider_names = get_configured_provider_names(config)
    for provider_name in configured_provider_names:
        if provider_name not in loaded_provider_names:
            logger.warning(
                f"Provider '{provider_name}' is configured but was not loaded. "
                "Ensure it is enabled and the implementation is correct."
            )
    return enabled_providers


def get_configured_provider_names(config: Config) -> List[str]:
    """
    Gets the names of all provider sections in the config file that are marked as enabled.
    """
    provider_names = []
    non_provider_sections = {"moodle", "ai", "notification"}
    for section in config.config.sections():
        if section not in non_provider_sections and config.config.has_option(
            section, "enabled"
        ):
            if config.config.getboolean(section, "enabled"):
                provider_names.append(section)
    return provider_names


__all__ = [
    "DiscordProvider",
    "PushbulletProvider",
    "WebhookSiteProvider",
    "initialize_providers",
]
