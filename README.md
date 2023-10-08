# Moodle Mate

## Overview

`Moodle-Mate` is a Python program designed to fetch Moodle notifications at regular intervals (60 seconds), summarize their content using GPT-3, and send the summarized notifications via Pushbullet to your smartphone and via a webhook to Discord.

## Dependencies

- Custom wrappers for the following APIs:
    - MoodleAPI
    - OpenAI
    - Pushbullet
    - Discord
- Beautiful Soup 4

## Installation

Clone the repository and install the required Python packages:

```
git clone https://github.com/EvickaStudio/Moodle-Mate.git
cd moodleStalker
pip install -r requirements.txt
```

## Configuration

A configuration file, `config.ini`, is required and should contain the following keys:

- Moodle URL (e.g. https://moodle.example.com)
- Moodle credentials (username, password)
- OpenAi API key
- Pushbullet API key
- Discord webhook URL
- systemMessage for GPT-3 (default in german)

## Usage

Run the script as follows:

```
python main.py
```

## Classes

### `MoodleNotificationHandler`

Manages the fetching of Moodle notifications for a specific user.

#### Methods

- `fetch_latest_notification()`: Fetches the latest notification.
- `fetch_newest_notification()`: Fetches the newest unread notification.
- `user_id_from(useridfrom)`: Retrieves information about a user from their ID. (naming is bad, i know)

### `NotificationSummarizer`

Summarizes text using the OpenAI API.

#### Methods

- `summarize(text)`: Summarizes the provided text.

### `NotificationSender`

Responsible for sending notifications to various platforms.

#### Methods

- `send(subject, text, summary, useridfrom)`: Sends a notification to Pushbullet and Discord.

## Screenshots

![Discord](images/discord.jpg)

## Author

EvickaStudio

