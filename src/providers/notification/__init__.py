import logging
from typing import List

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider
from src.core.plugin_manager import PluginManager

from .discord.provider import DiscordProvider
from .gotify.provider import GotifyProvider
from .pushbullet.provider import PushbulletProvider
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

    # Initialize Pushbullet provider if enabled
    if hasattr(config, "pushbullet") and config.pushbullet.enabled:
        logger.info("Initializing Pushbullet provider")
        providers.append(
            PushbulletProvider(
                api_key=config.pushbullet.api_key,
                include_summary=config.pushbullet.include_summary,
            )
        )
        already_loaded_providers.add("pushbullet")

    # Initialize Gotify provider if enabled
    if hasattr(config, "gotify") and config.gotify.enabled:
        logger.info("Initializing Gotify provider")
        providers.append(
            GotifyProvider(
                server_url=config.gotify.server_url,
                app_token=config.gotify.app_token,
                priority=config.gotify.priority,
                include_summary=config.gotify.include_summary,
                use_markdown=config.gotify.use_markdown,
            )
        )
        already_loaded_providers.add("gotify")

    # Initialize dynamic providers from plugins
    plugin_manager = PluginManager()
    plugin_providers = plugin_manager.get_notification_providers()

    for provider_name, provider_class in plugin_providers.items():
        if provider_name in already_loaded_providers:
            logger.warning(
                f"Skipping plugin provider '{provider_name}' as it conflicts with a built-in provider"
            )
            continue

        if hasattr(config, provider_name) and getattr(config, provider_name).enabled:
            logger.info(f"Initializing plugin provider: {provider_name}")
            provider_config = getattr(config, provider_name)
            # Convert provider_config to dict and remove 'enabled' key
            config_dict = {
                k: v for k, v in provider_config.__dict__.items() if k != "enabled"
            }
            providers.append(provider_class(**config_dict))
            already_loaded_providers.add(provider_name)

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
    "GotifyProvider",
    "PushbulletProvider",
    "WebhookSiteProvider",
    "initialize_providers",
]
