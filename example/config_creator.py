# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Config File Creator for Moodle Mate
Professional utility for configuring Moodle Mate, a tool for receiving Moodle notifications via various services.

Author: EvickaStudio
Date: 25.12.2023
Github: @EvickaStudio
"""

import configparser

from ui.screen import old_logo


def create_config_file():
    config = configparser.ConfigParser()

    # Display the logo and introductory information
    print(old_logo)
    print(
        """
        Moodle Mate Configuration Utility
        ----------------------------------
        Moodle Mate streamlines the process of receiving Moodle notifications and summaries across different platforms.
        This utility facilitates the creation of a robust configuration file for Moodle Mate.
        """
    )

    # Gather Moodle connection details
    moodleUrl = input(
        "Enter Moodle site URL (e.g., https://subdomain.example.com/ the login site):\nMoodle URL: "
    )
    username = input("\nEnter Moodle username you use to log in to Moodle: ")
    password = input("\nEnter Moodle password: ")

    # Setup for Pushbullet notifications
    pushbullet_enabled = input(
        "\nPushbullet enables notification mirroring and sending to your PC or mobile device via its application. Would you like to integrate Pushbullet into this service? (1: Yes, 0: No): "
    )
    if pushbullet_enabled == "1":
        pushbulletkey = input("Enter Pushbullet API key: ")
    else:
        pushbulletkey = ""
        pushbullet_enabled = "0"

    # Setup for Discord Webhook notifications
    discord_webhook_enabled = input(
        "\nEnable Discord webhook for notifications? (1: Yes, 0: No): "
    )
    if discord_webhook_enabled == "1":
        webhookurl = input("Enter Discord webhook URL: ")
    else:
        webhookurl = ""
        discord_webhook_enabled = "0"

    # Configuration for message summarization using GPT
    summarize_enabled = input(
        "\nEnable message summarization through GPT? (1: Yes, 0: No): "
    )
    if summarize_enabled == "1":
        # Define standard system messages
        systemMessageTemplates = {
            "DE1": "Bitte fassen Sie den folgenden Text umfassend und qualitativ hochwertig zusammen. Zusammenfassung sollte 1-2 Sätze umfassen.",
            "DE2": "Deine Rolle ist es, als Assistent für ein Programm namens MoodleMate zu agieren. Deine Hauptaufgabe ist es, eingehende Nachrichten für mobile Benachrichtigungen zusammenzufassen. Auf Aufforderung wirst du prägnante, hochwertige Zusammenfassungen des bereitgestellten Textes liefern, idealerweise in 1-2 Sätzen. Dein Ziel ist es, die Essenz der Nachricht genau und knapp einzufangen, ideal für schnelle mobile Benachrichtigungen. Es ist wichtig, die ursprüngliche Absicht und die Schlüsseldetails der Nachricht beizubehalten, während du sie in ein kürzeres Format kondensierst. Dabei solltest du unnötige Details oder Füllinhalte vermeiden und dich ausschließlich auf die Kernbotschaft konzentrieren. Außerdem solltest du in allen Zusammenfassungen einen neutralen und professionellen Ton beibehalten. Wenn nötig, solltest du die Nachricht auch ins Deutsche übersetzen.  Füge passende Emojis hinzu.",
            "EN": "Please summarize the following text comprehensively. The summary should be concise and 1-2 sentences long.",
        }

        # Prompt for system message template selection or custom input
        for key in systemMessageTemplates:
            print(f"{key}: {systemMessageTemplates[key]}")
        prompt_choice = input(
            f"\nSelect a system prompt for GPT summarization:\n DE1, DE2, EN, or Custom (Enter Custom for your own prompt): "
        )
        if prompt_choice in systemMessageTemplates:
            systemMessage = systemMessageTemplates[prompt_choice]
        else:
            systemMessage = input("Enter your custom system prompt: ")

        # Option to use FakeOpen as an alternative to OpenAI
        fakeopen_enabled = input(
            "\nWould you prefer to use FakeOpen, a complimentary alternative to OpenAI? Please note that I advise against it due to potential compatibility issues with my server (likely IP-related) and its general instability (frequent failures in API calls, often due to depleted or overused API keys).  (1: Yes, 0: No): "
        )
        fakeopen_enabled = "1" if fakeopen_enabled == "1" else "0"

        if fakeopen_enabled == "0":
            openaikey = input("\nEnter OpenAI API key with available balance: ")
        else:
            openaikey = ""

        # GPT model selection
        print(
            """
            GPT Model Selection (as of 25.12.2023):
            1. GPT4 Turbo - Recommended for speed and cost-efficiency
                Input: $0.01 / 1K tokens
                Output: $0.03 / 1K tokens
            2. GPT4 - Standard GPT4 model
                Input: $0.03 / 1K tokens
                Output: $0.06 / 1K tokens
            3. GPT 3.5 Turbo - Most cost-effective option
                Input: $0.0010 / 1K tokens
                Output: $0.0020 / 1K tokens
        """
        )
        model_choice = input("Choose a GPT model (1, 2, or 3): ")
        model = {
            "1": "gpt-4-1106-preview",
            "2": "gpt-4",
            "3": "gpt-3.5-turbo-1106",
        }.get(model_choice, "")
    else:
        summarize_enabled = "0"
        systemMessage = ""
        fakeopen_enabled = "0"
        model = ""

    # Construct configuration dictionary
    config["moodle"] = {
        "moodleUrl": moodleUrl,
        "username": username,
        "password": password,
        "openaikey": openaikey,
        "pushbulletkey": pushbulletkey,
        "pushbulletState": pushbullet_enabled,
        "webhookState": discord_webhook_enabled,
        "webhookUrl": webhookurl,
        "systemMessage": f'"{systemMessage}"',
        "model": model,
        "fakeopen": fakeopen_enabled,
        "summary": summarize_enabled,
    }

    # Write configuration to file
    with open("config.ini", "w", encoding="utf-8") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    try:
        create_config_file()
        print("Configuration file created successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
