import configparser
import logging
from pathlib import Path
from typing import Any, Optional

from .schema import (
    AIConfig,
    DiscordConfig,
    FiltersConfig,
    HealthConfig,
    MoodleConfig,
    NotificationConfig,
    ProviderConfig,
    PushbulletConfig,
    WebhookSiteConfig,
    WebUIConfig,
)


class Config:
    """Configuration manager for MoodleMate."""

    _instance = None

    def __new__(cls, config_path: str = "config.ini"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.config_path = config_path
            cls._instance._init_config(config_path)
        return cls._instance

    def reload(self) -> None:
        """Reloads the configuration from the config file."""
        logging.info("Reloading configuration from %s", self.config_path)
        self._init_config(self.config_path)

    def _init_config(self, config_path: str):
        """Initialize configuration from file."""
        self.config = configparser.ConfigParser()
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        self.config.read(config_path)

        # Initialize config sections
        self.moodle = self._load_moodle_config()
        self.ai = self._load_ai_config()
        self.notification = self._load_notification_config()
        self.filters = self._load_filters_config()
        self.health = self._load_health_config()
        self.webui = self._load_webui_config()

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
            initial_fetch_count=int(
                self._get_config("moodle", "initial_fetch_count", "1")
            ),
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
                "ai", "endpoint", None
            ),  # uses openai as fallback
        )

    def _load_notification_config(self) -> NotificationConfig:
        """Load notification configuration."""
        return NotificationConfig(
            max_retries=int(self._get_config("notification", "max_retries", "5")),
            fetch_interval=int(
                self._get_config("notification", "fetch_interval", "60")
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

    def _load_filters_config(self) -> FiltersConfig:
        """Load Filters configuration."""
        return FiltersConfig(
            ignore_subjects_containing=self._get_list(
                "filters", "ignore_subjects_containing"
            ),
            ignore_courses_by_id=self._get_int_list("filters", "ignore_courses_by_id"),
        )

    def _load_health_config(self) -> HealthConfig:
        """Load Health configuration."""
        return HealthConfig(
            enabled=self._get_bool("health", "enabled", False),
            heartbeat_interval=self._get_int_or_none("health", "heartbeat_interval"),
            failure_alert_threshold=self._get_int_or_none(
                "health", "failure_alert_threshold"
            ),
            target_provider=self._get_config("health", "target_provider", None),
        )

    def _load_webui_config(self) -> WebUIConfig:
        """Load WebUI configuration."""
        return WebUIConfig(
            enabled=self._get_bool("webui", "enabled", False),
            password=self._get_config("webui", "password", ""),
        )

    def _get_list(self, section: str, key: str) -> list[str]:
        """Get a list of strings from config."""
        value = self._get_config(section, key, "")
        return [item.strip() for item in value.split(",")] if value else []

    def _get_int_list(self, section: str, key: str) -> list[int]:
        """Get a list of integers from config."""
        value = self._get_config(section, key, "")
        return [int(item.strip()) for item in value.split(",")] if value else []

    def _get_int_or_none(self, section: str, key: str) -> Optional[int]:
        """Get an integer from config, or None if not present/empty."""
        value = self._get_config(section, key)
        return int(value) if value else None

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
                "filters",
                "health",
                "webui",
            ]:
                continue

            # Check if this section has an 'enabled' option
            if self.config.has_option(section, "enabled"):
                # Create a dynamic provider config
                provider_config = ProviderConfig(
                    enabled=self._get_bool(section, "enabled", False)
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
