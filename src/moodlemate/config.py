from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MoodleConfig(BaseModel):
    """Moodle connection and notification bootstrap settings."""

    url: str
    username: str
    password: str
    initial_fetch_count: int = 1


class AIConfig(BaseModel):
    """AI summarization configuration."""

    enabled: bool = True
    api_key: str = ""
    model: str = "gpt-5-nano"
    temperature: float = 0.7
    max_tokens: int = 150
    system_prompt: str = "Summarize the message concisely with appropriate emojis, excluding links. Write in target language of the notification."
    endpoint: str | None = None


class NotificationConfig(BaseModel):
    """Polling and HTTP retry behavior for notification fetching/sending."""

    max_retries: int = Field(default=5, ge=0, le=10)
    fetch_interval: int = Field(default=60, ge=10, le=3600)
    connect_timeout: float = Field(default=10.0, gt=0, le=60)
    read_timeout: float = Field(default=30.0, gt=0, le=180)
    retry_total: int = Field(default=3, ge=0, le=10)
    retry_backoff_factor: float = Field(default=1.0, ge=0.0, le=5.0)
    max_payload_bytes: int = Field(default=65536, ge=1024, le=262144)


class FiltersConfig(BaseModel):
    """Notification filtering rules."""

    ignore_subjects_containing: list[str] = Field(default_factory=list)
    ignore_courses_by_id: list[int] = Field(default_factory=list)


class HealthConfig(BaseModel):
    """Health monitoring and alert routing settings."""

    enabled: bool = False
    heartbeat_interval: int | None = None
    failure_alert_threshold: int | None = None
    target_provider: str | None = None


class WebConfig(BaseModel):
    """Embedded Web UI settings."""

    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 9095
    auth_secret: str | None = None


# Providers
class DiscordConfig(BaseModel):
    """Discord provider settings."""

    enabled: bool = False
    webhook_url: str = ""
    bot_name: str = "MoodleMate"
    thumbnail_url: str = ""


class WebhookSiteConfig(BaseModel):
    """Webhook.site provider settings."""

    enabled: bool = False
    webhook_url: str = ""
    include_summary: bool = True


class PushbulletConfig(BaseModel):
    """Pushbullet provider settings."""

    enabled: bool = False
    api_key: str = ""
    include_summary: bool = True


class Settings(BaseSettings):
    """Application settings loaded from environment variables and `.env`."""

    model_config = SettingsConfigDict(
        env_prefix="MOODLEMATE_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    moodle: MoodleConfig
    ai: AIConfig = Field(default_factory=AIConfig)
    notification: NotificationConfig = Field(default_factory=NotificationConfig)
    filters: FiltersConfig = Field(default_factory=FiltersConfig)
    health: HealthConfig = Field(default_factory=HealthConfig)
    web: WebConfig = Field(default_factory=WebConfig)

    # Providers
    # To add a new provider, define its config model above and add it here.
    discord: DiscordConfig = Field(default_factory=DiscordConfig)
    webhook_site: WebhookSiteConfig = Field(default_factory=WebhookSiteConfig)
    pushbullet: PushbulletConfig = Field(default_factory=PushbulletConfig)

    # Runtime/session security
    session_encryption_key: str | None = None
