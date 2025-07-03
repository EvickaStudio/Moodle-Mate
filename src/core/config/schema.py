from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MoodleConfig:
    url: str
    username: str
    password: str
    initial_fetch_count: int = 1


@dataclass
class AIConfig:
    enabled: bool = True
    api_key: str = ""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 150
    system_prompt: str = (
        "Summarize the message concisely with appropriate emojis, excluding links."
    )
    endpoint: Optional[str] = None


@dataclass
class NotificationConfig:
    max_retries: int = 5
    fetch_interval: int = 60


@dataclass
class DiscordConfig:
    enabled: bool = False
    webhook_url: str = ""
    bot_name: str = "MoodleMate"
    thumbnail_url: str = ""


@dataclass
class WebhookSiteConfig:
    """Configuration for Webhook.site notification provider."""

    enabled: bool = False
    webhook_url: str = ""
    include_summary: bool = True


@dataclass
class PushbulletConfig:
    """Configuration for Pushbullet notification provider."""

    enabled: bool = False
    api_key: str = ""
    include_summary: bool = True


@dataclass
class ProviderConfig:
    """Dynamic configuration for notification providers.

    This class is used for dynamically loaded providers that don't have
    a predefined configuration structure.
    """

    enabled: bool = False
    # Additional attributes will be added dynamically


@dataclass
class FiltersConfig:
    """Configuration for notification filters."""

    ignore_subjects_containing: list[str] = field(default_factory=list)
    ignore_courses_by_id: list[int] = field(default_factory=list)


@dataclass
class HealthConfig:
    """Configuration for health and status notifications."""

    enabled: bool = False
    heartbeat_interval: Optional[int] = None
    failure_alert_threshold: Optional[int] = None
    target_provider: Optional[str] = None


@dataclass
class WebUIConfig:
    """Configuration for the Web UI."""

    enabled: bool = False
    password: str = ""
