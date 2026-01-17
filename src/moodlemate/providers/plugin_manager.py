import importlib
import inspect
import logging
import pkgutil
from typing import TYPE_CHECKING

from moodlemate.notifications.base import NotificationProvider

if TYPE_CHECKING:
    from moodlemate.config import Settings

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages discovery and loading of notification provider plugins."""

    @classmethod
    def discover_providers(cls) -> dict[str, type[NotificationProvider]]:
        """Discover all available notification provider classes.

        Returns:
            Dict mapping provider names to provider classes
        """
        from moodlemate.providers import notification

        providers = {}

        # Walk through the notification providers package
        for _, name, is_pkg in pkgutil.iter_modules(notification.__path__):
            if is_pkg:
                try:
                    # Import the provider module
                    module = importlib.import_module(
                        f"moodlemate.providers.notification.{name}.provider"
                    )

                    # Find provider classes in the module
                    for _item_name, item in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(item, NotificationProvider)
                            and item is not NotificationProvider
                        ):
                            providers[name] = item
                            logger.info(f"Discovered provider: {name}")
                except Exception as e:
                    logger.error(f"Error loading provider {name}: {e!s}")

        return providers

    @classmethod
    def load_enabled_providers(cls, settings: "Settings") -> list[NotificationProvider]:
        """Load all enabled notification providers from configuration.

        Args:
            settings: Application configuration

        Returns:
            List of initialized provider instances
        """
        providers = []
        discovered = cls.discover_providers()

        # Check each discovered provider if it's enabled in settings
        for name, provider_class in discovered.items():
            try:
                if hasattr(settings, name):
                    provider_settings = getattr(settings, name)
                    if (
                        hasattr(provider_settings, "enabled")
                        and provider_settings.enabled
                    ):
                        # Get provider-specific config as dict, excluding 'enabled'
                        config_dict = provider_settings.model_dump(exclude={"enabled"})

                        # Initialize the provider with its config
                        provider = provider_class(**config_dict)
                        provider.provider_name = name.lower()
                        providers.append(provider)
                        logger.info(f"Loaded enabled provider: {name}")
            except Exception as e:
                logger.error(f"Error initializing provider {name}: {e!s}")

        return providers
