import configparser
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def prompt_input(
    prompt: str, required: bool = False, default: Optional[str] = None
) -> str:
    """
    Prompts the user for input, ensuring required fields are filled.
    """
    while True:
        value = input(prompt).strip()
        if not value and default is not None:
            return default
        elif not value and required:
            print("This field is required. Please enter a value.")
        else:
            return value


def get_moodle_config() -> Dict[str, str]:
    """
    Collects Moodle configuration from the user.
    """
    moodle_url = prompt_input(
        "Enter Moodle site URL (e.g., https://subdomain.example.com/):\nMoodle URL: ",
        required=True,
    )
    moodle_username = prompt_input(
        "Enter Moodle username you use to log in to Moodle: ", required=True
    )
    moodle_password = prompt_input("Enter Moodle password: ", required=True)

    return {
        "MOODLE_URL": moodle_url,
        "MOODLE_USERNAME": moodle_username,
        "MOODLE_PASSWORD": moodle_password,
    }


def get_pushbullet_config() -> Dict[str, str]:
    """
    Collects Pushbullet configuration from the user.
    """
    enabled = prompt_input(
        "\nEnable Pushbullet notifications? (1: Yes, 0: No): ", required=True
    )
    if enabled == "1":
        api_key = prompt_input("Enter Pushbullet API key: ", required=True)
    else:
        api_key = ""
        enabled = "0"
    return {"ENABLED": enabled, "PUSHBULLET_API_KEY": api_key}


def get_discord_config() -> Dict[str, str]:
    """
    Collects Discord configuration from the user.
    """
    enabled = prompt_input(
        "\nEnable Discord webhook for notifications? (1: Yes, 0: No): ",
        required=True,
    )
    if enabled == "1":
        webhook_url = prompt_input("Enter Discord webhook URL: ", required=True)
        bot_name = prompt_input(
            "Enter name of the bot as displayed in Discord (default 'MoodleMate'): ",
            default="MoodleMate",
        )
        thumbnail_url = prompt_input(
            "Enter Thumbnail URL for Discord messages (e.g., favicon URL): "
        )
    else:
        webhook_url = ""
        bot_name = ""
        thumbnail_url = ""
        enabled = "0"
    return {
        "ENABLED": enabled,
        "WEBHOOK_URL": webhook_url,
        "BOT_NAME": bot_name,
        "THUMBNAIL_URL": thumbnail_url,
    }


def get_summary_config() -> Dict[str, str]:
    """
    Collects summarization configuration from the user.
    """
    summary_config = {}
    summarize = prompt_input(
        "\nEnable message summarization through AI? (1: Yes, 0: No): ",
        required=True,
    )
    if summarize == "1":
        openai_api_endpoint = prompt_input(
            "Enter OpenAI API endpoint (default 'https://api.openai.com/v1/chat/completions'): ",
            default="https://api.openai.com/v1/chat/completions",
        )
        openai_api_key = prompt_input(
            "Enter OpenAI API key with available balance: ", required=True
        )

        # GPT model selection
        print(
            """
        GPT Model Selection:
        1. gpt-4o-mini
        2. gpt-4o
        3. Custom model
        """
        )
        model_choice = prompt_input(
            "Choose a GPT model (1, 2, or 3): ", required=True
        )
        if model_choice == "1":
            model = "gpt-4o-mini"
        elif model_choice == "2":
            model = "gpt-4o"
        elif model_choice == "3":
            model = prompt_input("Enter custom model: ", required=True)
        else:
            print("Invalid choice. Defaulting to 'gpt-4o-mini'")
            model = "gpt-4o-mini"

        # System prompt selection
        system_message_templates = {
            "DE1": "Bitte fassen Sie den folgenden Text umfassend und qualitativ hochwertig zusammen. Zusammenfassung sollte 1-2 Sätze umfassen.",
            "DE2": "Du bist ein Assistent. Deine Aufgabe ist es, eingehende Nachrichten prägnant zusammenzufassen. Dein Ziel ist eine knappe, jedoch präzise Darstellung des Originaltextes, ohne Wiederholungen. Halte dich also kurz und verwende passende Emojis. Gebe keine Links aus",
            "EN": "Please summarize the following text comprehensively. The summary should be concise and 1-2 sentences long.",
        }
        print("\nAvailable system prompts:")
        for key, message in system_message_templates.items():
            print(f"{key}: {message}")
        prompt_choice = prompt_input(
            "Select a system prompt (DE1, DE2, EN) or enter 'Custom' to provide your own: ",
            required=True,
        )
        if prompt_choice in system_message_templates:
            system_prompt = system_message_templates[prompt_choice]
        else:
            system_prompt = prompt_input(
                "Enter your custom system prompt: ", required=True
            )

        # Assign to config
        summary_config["SUMMARIZE"] = "1"
        summary_config["OPENAI_API_ENDPOINT"] = openai_api_endpoint
        summary_config["OPENAI_API_KEY"] = openai_api_key
        summary_config["MODEL"] = model
        summary_config["SYSTEM_PROMPT"] = system_prompt
    else:
        summary_config["SUMMARIZE"] = "0"
        summary_config["OPENAI_API_ENDPOINT"] = ""
        summary_config["OPENAI_API_KEY"] = ""
        summary_config["MODEL"] = ""
        summary_config["SYSTEM_PROMPT"] = ""
    return summary_config


def get_settings_config() -> Dict[str, str]:
    """
    Collects general settings from the user.
    """
    fetch_interval = prompt_input(
        "\nEnter interval in seconds to fetch new messages from Moodle (default 60): ",
        default="60",
    )
    max_retries = prompt_input(
        "Enter maximum number of retries to fetch new messages before giving up (default 5): ",
        default="5",
    )
    return {"FETCH_INTERVAL": fetch_interval, "MAX_RETRIES": max_retries}


def create_config_file():
    try:
        config = configparser.ConfigParser()

        # Display the logo and introductory information
        print(
            """
            Moodle Mate Configuration Utility
            ----------------------------------
            Moodle Mate streamlines the process of receiving Moodle notifications and summaries across different platforms.
            This utility facilitates the creation of a robust configuration file for Moodle Mate.
            """
        )

        # Gather configurations
        moodle_config = get_moodle_config()
        pushbullet_config = get_pushbullet_config()
        discord_config = get_discord_config()
        summary_config = get_summary_config()
        settings_config = get_settings_config()

        # Construct configuration dictionary
        config["moodle"] = moodle_config
        config["pushbullet"] = pushbullet_config
        config["discord"] = discord_config
        config["summary"] = summary_config
        config["settings"] = settings_config

        # Write configuration to file
        with open("config.ini", "w", encoding="utf-8") as configfile:
            config.write(configfile)

        print("Configuration file created successfully.")

    except Exception as e:
        logger.exception(
            "An error occurred while creating the configuration file."
        )
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    create_config_file()
