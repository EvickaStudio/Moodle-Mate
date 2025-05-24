import configparser
import logging
from pathlib import Path
from typing import Any

from .schema import (
    AIConfig,
    DiscordConfig,
    MoodleConfig,
    NotificationConfig,
    ProviderConfig,
    PushbulletConfig,
    WebhookSiteConfig,
)


class Config:
    """
    Manages the application's configuration settings, loaded from a `config.ini` file.

    This class implements a singleton pattern to ensure that configuration is loaded
    only once. It parses the `config.ini` file and maps its sections and keys to
    strongly-typed dataclass objects (e.g., `MoodleConfig`, `AIConfig`).

    The configuration includes settings for Moodle connectivity, AI summarization,
    general notification behavior, and specific settings for various notification
    providers (both built-in and dynamically discovered plugins).

    Access to configuration values is typically done through attributes named after
    the sections in the .ini file, for example:
    `config.moodle.url`, `config.ai.api_key`, `config.discord.webhook_url`.

    Attributes:
        config (configparser.ConfigParser): The raw ConfigParser object holding all data.
        moodle (MoodleConfig): Configuration for Moodle connection.
        ai (AIConfig): Configuration for AI features (e.g., OpenAI).
        notification (NotificationConfig): General notification settings.
        discord (DiscordConfig): Configuration for Discord notifications.
        webhook_site (WebhookSiteConfig): Configuration for Webhook.site notifications.
        pushbullet (PushbulletConfig): Configuration for Pushbullet notifications.
        Additionally, attributes for dynamically loaded provider configurations are
        set (e.g., `self.slack`, `self.ntfy` if configured).

    Raises:
        FileNotFoundError: If the specified `config_path` (default `config.ini`)
                           does not exist during initialization.

    Example:
        >>> try:
        ...     app_config = Config() # Loads from 'config.ini' by default
        ...     print(f"Moodle URL: {app_config.moodle.url}")
        ...     if app_config.discord.enabled:
        ...         print(f"Discord Webhook: {app_config.discord.webhook_url}")
        ... except FileNotFoundError:
        ...     print("Config file not found. Please generate one.")
    """

    _instance = None

    def __new__(cls, config_path: str = "config.ini") -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config(config_path)
        return cls._instance

    def _init_config(self, config_path: str):
        """Initialize configuration from file."""
        if not isinstance(config_path, str):
            raise TypeError("config_path must be a string.")
        if not config_path:
            raise ValueError("config_path must not be empty.")

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
        self.pushbullet = self._load_pushbullet_config()

        # Load dynamic provider configurations
        self._load_provider_configs()

    def _get_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback to default."""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default

    def _get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """Get boolean configuration value."""
        value = self._get_config(section, key, str(int(default)))
        return value.lower() in ("1", "true", "yes", "on")

    def _load_moodle_config(self) -> MoodleConfig:
        """Load Moodle configuration."""
        return MoodleConfig(
            url=self._get_config("moodle", "url", ""),
            username=self._get_config("moodle", "username", ""),
            password=self._get_config("moodle", "password", ""),
        )

    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration."""
        return AIConfig(
            enabled=self._get_bool("ai", "enabled", True),
            api_key=self._get_config("ai", "api_key", ""),
            model=self._get_config("ai", "model", "gpt-4"),
            temperature=float(self._get_config("ai", "temperature", "0.7")),
            max_tokens=int(self._get_config("ai", "max_tokens", "150")),
            system_prompt=self._get_config(
                "ai",
                "system_prompt",
                "Summarize the message concisely with appropriate emojis, excluding links.",
            ),
            endpoint=self._get_config(
                "ai",
                "endpoint",
                None,
            ),  # uses openai as fallback
        )

    def _load_notification_config(self) -> NotificationConfig:
        """Load notification configuration."""
        return NotificationConfig(
            max_retries=int(self._get_config("notification", "max_retries", "5")),
            fetch_interval=int(
                self._get_config("notification", "fetch_interval", "60"),
            ),
        )

    def _load_discord_config(self) -> DiscordConfig:
        """Load Discord configuration."""
        return DiscordConfig(
            enabled=self._get_bool("discord", "enabled", False),
            webhook_url=self._get_config("discord", "webhook_url", ""),
            bot_name=self._get_config("discord", "bot_name", "MoodleMate"),
            thumbnail_url=self._get_config("discord", "thumbnail_url", ""),
        )

    def _load_webhook_site_config(self) -> WebhookSiteConfig:
        """Load Webhook.site configuration."""
        return WebhookSiteConfig(
            enabled=self._get_bool("webhook_site", "enabled", False),
            webhook_url=self._get_config("webhook_site", "webhook_url", ""),
            include_summary=self._get_bool("webhook_site", "include_summary", True),
        )

    def _load_pushbullet_config(self) -> PushbulletConfig:
        """Load Pushbullet configuration."""
        return PushbulletConfig(
            enabled=self._get_bool("pushbullet", "enabled", False),
            api_key=self._get_config("pushbullet", "api_key", ""),
            include_summary=self._get_bool("pushbullet", "include_summary", True),
        )

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
                "pushbullet",
            ]:
                continue

            # Check if this section has an 'enabled' option
            if self.config.has_option(section, "enabled"):
                # Create a dynamic provider config
                provider_config = ProviderConfig(
                    enabled=self._get_bool(section, "enabled", False),
                )

                # Add all other options from this section
                for option in self.config.options(section):
                    if option != "enabled":
                        setattr(
                            provider_config,
                            option,
                            self._get_config(section, option, ""),
                        )

                # Set the config on the main config object
                setattr(self, section, provider_config)
                # logging.info(f"Loaded dynamic provider config: {section}")
                logging.info(f"Found provider config for {section} in config.ini")
