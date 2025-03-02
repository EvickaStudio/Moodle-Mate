import importlib
import inspect
import logging
import pkgutil
from typing import Dict, List, Optional, Type

from src.core.config.loader import Config
from src.core.notification.base import NotificationProvider

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
    def load_enabled_providers(
        cls, config: Config, already_loaded: Optional[set] = None
    ) -> List[NotificationProvider]:
        """Load all enabled notification providers from configuration.

        Args:
            config: Application configuration
            already_loaded: Set of provider names that have already been loaded

        Returns:
            List of initialized provider instances
        """
        providers = []
        discovered = cls.discover_providers()
        already_loaded = already_loaded or set()

        # Check each discovered provider if it's enabled in config
        for name, provider_class in discovered.items():
            try:
                # Skip if this provider has already been loaded
                if name in already_loaded:
                    logger.info(f"Skipping already loaded provider: {name}")
                    continue

                # Check if this provider is enabled in config
                if hasattr(config, name) and getattr(config, name).enabled:
                    # Get provider-specific config
                    provider_config = getattr(config, name)

                    # Convert to dictionary for easier handling
                    config_dict = {
                        k: getattr(provider_config, k)
                        for k in dir(provider_config)
                        if not k.startswith("_") and k != "enabled"
                    }

                    # Initialize the provider with its config
                    provider = provider_class(**config_dict)
                    providers.append(provider)
                    already_loaded.add(name)  # Add to already loaded set
                    logger.info(f"Loaded enabled provider: {name}")
            except Exception as e:
                logger.error(f"Error initializing provider {name}: {str(e)}")

        return providers
