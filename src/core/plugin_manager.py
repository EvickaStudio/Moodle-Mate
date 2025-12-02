import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Type, TYPE_CHECKING

from src.core.notification.base import NotificationProvider

if TYPE_CHECKING:
    from src.config import Settings

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages discovery and loading of notification provider plugins."""

    @classmethod
    def discover_providers(cls) -> Dict[str, Type[NotificationProvider]]:
        """Discover all available notification provider classes.

        Returns:
            Dict mapping provider names to provider classes
        """
        from src.providers import notification

        providers = {}

        # Walk through the notification providers package
        for _, name, is_pkg in pkgutil.iter_modules(notification.__path__):
            if is_pkg:
                try:
                    # Import the provider module
                    module = importlib.import_module(
                        f"src.providers.notification.{name}.provider"
                    )

                    # Find provider classes in the module
                    for item_name, item in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(item, NotificationProvider)
                            and item is not NotificationProvider
                        ):
                            providers[name] = item
                            logger.info(f"Discovered provider: {name}")
                except Exception as e:
                    logger.error(f"Error loading provider {name}: {str(e)}")

        return providers

    @classmethod
    def load_enabled_providers(cls, settings: "Settings") -> List[NotificationProvider]:
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
                        provider.provider_name = name
                        providers.append(provider)
                        logger.info(f"Loaded enabled provider: {name}")
            except Exception as e:
                logger.error(f"Error initializing provider {name}: {str(e)}")

        return providers
