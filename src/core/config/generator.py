import configparser
import importlib
import inspect
import logging
import os
import pkgutil
import re
from typing import Callable, Dict, Optional, Type

from src.core.notification.base import NotificationProvider


class ConfigGenerator:
    """Interactive configuration generator for MoodleMate."""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.webhook_pattern = re.compile(
            r"https://discord\.com/api/webhooks/\d+/[\w-]+"
        )
        self.api_key_pattern = re.compile(r"^sk-[A-Za-z0-9_-]{48,}$")

    def _discover_providers(
        self,
    ) -> Dict[str, Type[NotificationProvider]]:
        """Discover available notification providers."""
        providers: Dict[str, Type[NotificationProvider]] = {}

        try:
            # Import the notification package
            from src.providers import notification

            # Get built-in providers
            self._load_builtin_providers(providers)

            # Discover additional providers using the plugin system
            self._load_plugin_providers(providers, notification.__path__)

        except Exception as e:
            logging.error(f"Error discovering providers: {str(e)}")

        return providers

    def _load_builtin_providers(
        self, providers: Dict[str, Type[NotificationProvider]]
    ) -> None:
        """Load built-in notification providers."""
        for provider_name in ["discord", "pushbullet", "slack", "ntfy"]:
            try:
                module = importlib.import_module(
                    f"src.providers.notification.{provider_name}.provider"
                )
                self._extract_provider_classes(module, provider_name, providers)
            except ImportError:
                continue

    def _load_plugin_providers(
        self, providers: Dict[str, Type[NotificationProvider]], package_path
    ) -> None:
        """Load plugin notification providers."""
        for _, name, is_pkg in pkgutil.iter_modules(package_path):
            if is_pkg and name not in providers:
                try:
                    module = importlib.import_module(
                        f"src.providers.notification.{name}.provider"
                    )
                    self._extract_provider_classes(module, name, providers)
                except ImportError:
                    continue

    def _extract_provider_classes(
        self,
        module,
        provider_name: str,
        providers: Dict[str, Type[NotificationProvider]],
    ) -> None:
        """Extract notification provider classes from a module."""
        for item_name, item in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(item, NotificationProvider)
                and item is not NotificationProvider
            ):
                providers[provider_name] = item

    def generate_config(self) -> bool:
        """Generate configuration file interactively."""
        try:
            print("\n🔧 Welcome to MoodleMate Configuration Generator!")
            print("Let's set up your configuration step by step.\n")

            # Moodle Configuration
            self._configure_moodle()

            # AI Configuration
            self._configure_ai()

            # Notification Configuration
            self._configure_notification()

            # Built-in provider configurations
            self._configure_discord()
            self._configure_pushbullet()

            # Discover and configure additional providers
            self._configure_additional_providers()

            return self._save_config()

        except KeyboardInterrupt:
            print("\n\nConfiguration cancelled by user.")
            return False
        except Exception as e:
            logging.error(f"Error generating configuration: {e}")
            return False

    def _get_input(
        self,
        prompt: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool]] = None,
        optional: bool = False,
    ) -> str:
        """Get user input with validation.

        Args:
            prompt: Input prompt text
            default: Default value if no input provided
            validator: Optional validation function that takes a string and returns bool
            optional: Whether the field is optional
        """
        while True:
            if default:
                value = input(f"{prompt} [{default}]: ").strip()
            else:
                value = input(f"{prompt}: ").strip()

            if not value:
                if optional:
                    return ""
                print("This field cannot be empty. Please try again.")
                continue

            if validator and value and not validator(value):
                continue

            return value

    def _get_bool_input(self, prompt: str, default: bool = False) -> bool:
        """Get boolean input from user."""
        default_str = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            print("Please enter 'y' or 'n'")

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url.startswith(("http://", "https://")):
            print("URL must start with http:// or https://")
            return False
        return True

    def _validate_webhook(self, url: str) -> bool:
        """Validate Discord webhook URL."""
        if not self.webhook_pattern.match(url):
            print("Invalid Discord webhook URL format")
            return False
        return True

    def _validate_api_key(self, key: str) -> bool:
        """Validate OpenAI API key format."""
        if not self.api_key_pattern.match(key):
            print("Invalid API key format")
            return False
        return True

    def _configure_moodle(self):
        """Configure Moodle section."""
        print("\n📚 Moodle Configuration")
        print("-" * 50)

        self.config["moodle"] = {
            "url": self._get_input(
                "Enter your Moodle URL", validator=self._validate_url
            ),
            "username": self._get_input("Enter your Moodle username"),
            "password": self._get_input("Enter your Moodle password"),
        }

    def _configure_ai(self):
        """Configure AI section."""
        print("\n🤖 AI Configuration")
        print("-" * 50)

        enabled = self._get_bool_input("Enable AI summarization?", True)
        self.config["ai"] = {"enabled": "1" if enabled else "0"}

        if enabled:
            self.config["ai"].update(
                {
                    "api_key": self._get_input(
                        "Enter your OpenAI API key", validator=self._validate_api_key
                    ),
                    "model": self._get_input("Enter AI model name", "gpt-4o-mini"),
                    "temperature": self._get_input(
                        "Enter temperature (0.0-1.0)", "0.7"
                    ),
                    "max_tokens": self._get_input("Enter max tokens", "150"),
                    "system_prompt": self._get_input(
                        "Enter system prompt",
                        "Summarize the message concisely with appropriate emojis, excluding links.",
                    ),
                    "endpoint": self._get_input(
                        "Enter API endpoint (optional)",
                        "https://api.openai.com/v1/chat/completions",
                    ),
                }
            )

    def _configure_notification(self):
        """Configure notification section."""
        print("\n📬 Notification Configuration")
        print("-" * 50)

        self.config["notification"] = {
            "max_retries": self._get_input("Enter max retries", "5"),
            "fetch_interval": self._get_input("Enter fetch interval in seconds", "60"),
        }

    def _configure_discord(self):
        """Configure Discord section."""
        print("\n📱 Discord Configuration")
        print("-" * 50)

        enabled = self._get_bool_input("Enable Discord notifications?", True)
        self.config["discord"] = {"enabled": "1" if enabled else "0"}

        if enabled:
            self.config["discord"].update(
                {
                    "webhook_url": self._get_input(
                        "Enter Discord webhook URL", validator=self._validate_webhook
                    ),
                    "bot_name": self._get_input("Enter bot name", "MoodleMate"),
                    "thumbnail_url": self._get_input(
                        "Enter thumbnail URL (optional)", optional=True
                    ),
                }
            )

    def _configure_pushbullet(self):
        """Configure Pushbullet section."""
        print("\n📱 Pushbullet Configuration")
        print("-" * 50)

        enabled = self._get_bool_input("Enable Pushbullet notifications?", False)
        self.config["pushbullet"] = {"enabled": "1" if enabled else "0"}

        if enabled:
            self.config["pushbullet"].update(
                {"api_key": self._get_input("Enter Pushbullet API key")}
            )

    def _configure_additional_providers(self):
        """Discover and configure additional notification providers."""
        providers = self._discover_providers()

        # Skip built-in providers that are already configured
        for provider_name in ["discord", "pushbullet"]:
            if provider_name in providers:
                del providers[provider_name]

        if not providers:
            return

        print("\n🔌 Additional Notification Providers")
        print("-" * 50)
        print(f"Found {len(providers)} additional notification providers.")

        for name, provider_class in providers.items():
            print(f"\n📱 {name.capitalize()} Configuration")
            print("-" * 50)

            # Get provider description from docstring
            description = (
                provider_class.__doc__ or f"{name.capitalize()} notification provider"
            )
            print(f"{description}\n")

            enabled = self._get_bool_input(
                f"Enable {name.capitalize()} notifications?", False
            )
            self.config[name] = {"enabled": "1" if enabled else "0"}

            if enabled:
                # Get init parameters for the provider
                try:
                    init_params = inspect.signature(provider_class.__init__).parameters

                    # Skip self parameter
                    param_names = [p for p in init_params if p != "self"]

                    for param_name in param_names:
                        param = init_params[param_name]
                        # Check if parameter has a default value
                        has_default = param.default is not param.empty
                        default_value = param.default if has_default else ""

                        # Make parameter optional if it has a default value
                        value = self._get_input(
                            f"Enter {param_name.replace('_', ' ')}",
                            default_value if has_default else None,
                            optional=has_default,
                        )

                        if value or not has_default:
                            self.config[name][param_name] = value
                except Exception as e:
                    logging.error(f"Error configuring {name}: {str(e)}")
                    print(
                        f"Could not automatically configure {name}. Please check the documentation."
                    )

    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            config_path = "config.ini"
            if os.path.exists(config_path):
                backup = f"{config_path}.backup"
                os.rename(config_path, backup)
                print(f"\nExisting configuration backed up to {backup}")

            with open(config_path, "w") as configfile:
                self.config.write(configfile)

            print(f"\n✅ Configuration saved to {config_path}")
            return True

        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            return False
