<!--
 Copyright 2024 EvickaStudio

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

Example:

```ini
[moodle]
# Moodle Settings
# URL for Moodle API access
MOODLE_URL = https://subdomain.example.com/
# Username and password for Moodle login
MOODLE_USERNAME = 123456
MOODLE_PASSWORD = password

[summary]
# Summarization Settings
# Enable or disable summarization (1 = enabled, 0 = disabled)
SUMMARIZE = 1
# OpenAI API endpoint (e.g., https://api.openai.com/v1/chat/completions)
OPENAI_API_ENDPOINT = https://api.openai.com/v1/chat/completions
# OpenAI API key
OPENAI_API_KEY = sk-xxxxx
# Model to use for summarization (e.g., gpt-3.5-turbo, gpt-4)
MODEL = gpt-4o-mini
# System prompt for AI summarization
SYSTEM_PROMPT = "Du bist ein Assistent. Deine Aufgabe ist es, eingehende Nachrichten prägnant zusammenzufassen. Dein Ziel ist eine knappe, jedoch präzise Darstellung des Originaltextes, ohne Wiederholungen. Halte dich also kurz und verwende passende Emojis. Gebe keine Links aus"

[settings]
# General Settings
# Maximum number of retries to fetch new messages before giving up
MAX_RETRIES = 5
# Interval in seconds to fetch new messages from Moodle
FETCH_INTERVAL = 60

[pushbullet]
# Pushbullet Settings
# Enable or disable Pushbullet notifications (1 = enabled, 0 = disabled)
ENABLED = 0
# Pushbullet API key
PUSHBULLET_API_KEY = o.xxxxx

[discord]
# Discord Settings
# Enable or disable Discord notifications (1 = enabled, 0 = disabled)
ENABLED = 1
# Discord webhook URL
WEBHOOK_URL = https://discord.com/api/webhooks/1234567890/abcdefg
# Name of the bot as displayed in Discord
BOT_NAME = MoodleMate
# Thumbnail URL for Discord messages (e.g., favicon URL)
THUMBNAIL_URL = https://subdomain.example.com/favicon.ico

```
