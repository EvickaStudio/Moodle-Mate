import logging
from typing import List

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider
from src.core.plugin_manager import PluginManager

from .discord.provider import DiscordProvider
from .webhook_site.provider import WebhookSiteProvider

logger = logging.getLogger(__name__)


def initialize_providers(config: Config) -> List[NotificationProvider]:
    """Initialize enabled notification providers from config.

    This function initializes both built-in providers and dynamically
    discovered providers from the plugin system.

    Args:
        config: Application configuration

    Returns:
        List of initialized provider instances
    """
    providers = []
    already_loaded_providers = set()

    # Initialize Discord provider if enabled
    if hasattr(config, "discord") and config.discord.enabled:
        logger.info("Initializing Discord provider")
        providers.append(
            DiscordProvider(
                webhook_url=config.discord.webhook_url,
                bot_name=config.discord.bot_name,
                thumbnail_url=config.discord.thumbnail_url,
            )
        )
        already_loaded_providers.add("discord")

    # Initialize Webhook.site provider if enabled
    if hasattr(config, "webhook_site") and config.webhook_site.enabled:
        logger.info("Initializing Webhook.site provider")
        providers.append(
            WebhookSiteProvider(
                webhook_url=config.webhook_site.webhook_url,
                include_summary=config.webhook_site.include_summary,
            )
        )
        already_loaded_providers.add("webhook_site")

    # Load dynamically discovered providers
    try:
        # Pass the set of already loaded providers to avoid duplicates
        dynamic_providers = PluginManager.load_enabled_providers(
            config, already_loaded=already_loaded_providers
        )
        providers.extend(dynamic_providers)
    except Exception as e:
        logger.error(f"Error loading dynamic providers: {str(e)}")

    # Log warning for configured but missing providers
    for provider_name in get_configured_provider_names(config):
        if provider_name not in already_loaded_providers and provider_name != "discord":
            logger.warning(
                f"Provider '{provider_name}' is configured but not implemented or found"
            )

    logger.info(
        f"Initialized {len(providers)} notification providers: {[p.__class__.__name__ for p in providers]}"
    )
    return providers


def get_configured_provider_names(config: Config) -> List[str]:
    """Get names of all providers configured in config.ini."""
    provider_names = []

    # Get directly from the ConfigParser sections instead of Config object attributes
    non_provider_sections = {"moodle", "ai", "notification"}

    for section in config.config.sections():
        # Skip known non-provider sections
        if section not in non_provider_sections:
            # Check if this section has an 'enabled' option which providers should have
            if config.config.has_option(section, "enabled"):
                provider_names.append(section)

    return provider_names


__all__ = [
    "DiscordProvider",
    "WebhookSiteProvider",
    "initialize_providers",
]
