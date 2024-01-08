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

<div align="center">
  <img src="assets/logo.svg" alt="Logo" width="400"/>
  <h1>Moodle Mate</h1>
  <p><strong>Automated Moodle Notification Summarization</strong></p>
</div>

<p align="center">
  <a href="https://github.com/EvickaStudio/Moodle-Mate/actions"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/EvickaStudio/Moodle-Mate/ci.yml?+label=Build%20Status"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/blob/main/LICENSE.md"><img alt="GitHub license" src="https://img.shields.io/github/license/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/pulls"><img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/EvickaStudio/Moodle-Mate"></a>
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/EvickaStudio/Moodle-Mate">
  <a href="https://github.com/EvickaStudio/Moodle-Mate/watchers"><img alt="GitHub Watchers" src="https://img.shields.io/github/watchers/EvickaStudio/Moodle-Mate?style=flat&logo=github"></a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/EvickaStudio/Moodle-Mate">

---

> [!NOTE]
> I'm currently in the process of rewriting the codebase to make it more modular and easier to maintain. The current codebase is a mess and I'm sorry for that.
> Find the newest version in the `dev` branch.

## Contents

1. [Overview](#overview)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Documentation](#documentation)
7. [Screenshots](#screenshots)
8. [Contributing](#contributing)
9. [Author](#author)
10. [License](#author)

---

## <div id="overview">Overview</div>

Moodle Mate is an advanced Python application designed to streamline the process of receiving Moodle notifications. It fetches notifications from Moodle, summarizes them using GPT-3 or GPT-4 and sends them to the user via Pushbullet and Discord. The application is designed to run on a server and can be configured to run at specific intervals.

**Cost-Effective Operations**: Utilizes GPT-3.5-turbo for cost-effective operations (under 15 cents/month, excluding server costs).
Alternatively you could just disable summarization in the config file and use the script without GPT-3/4.

**NEW**: Moodle Mate now supports the OpenAI Assistant. This feature is currently under development and will be improved in future updates. Please be aware that the current version of the Assistant utilizes GPT-4 Turbo and is currently configured to provide summaries exclusively in German for now (with context). To use the Assistant, set the `test` variable in `NotificationSummarizer` to `True`:

Example:

```python
# utils > main_loop.py > main_loop()

# line 56, works [08.01.2024]
summary = summarizer.summarize(text, True)
```

**NEW**: implementation of fakeopen a free api for openai chat completion using gpt-4-32k. (not recommendet, as many chat completion requests are failing)

---

## <div id="dependencies">Dependencies</div>

The software relies on the following custom API wrappers and libraries:

- **MoodleAPI**: Interface for the Moodle API
- **OpenAI**: Interface for the OpenAI API
- **Pushbullet**: Interface for the Pushbullet API
- **Discord**: Utilizes webhooks for Discord integration.

---

## <div id="installation">Installation</div>

Clone the repository and install the Python packages:

```bash
git clone https://github.com/EvickaStudio/Moodle-Mate.git
cd Moodle-Mate
pip install -r requirements.txt
```

---

## <div id="configuration">Configuration</div>

A configuration file, `config.ini`, is necessary for the application's operation. It should contain:

- Moodle URL
- Moodle Username & Password
- OpenAI API Key
- Pushbullet API Key
- Pushbullet State (1: Activated, 0: Deactivated)
- Webhook State (1: Activated, 0: Deactivated)
- Discord Webhook URL
- System Message for GPT-3 (Default in German)
- Set GPT model, standard gpt-3.5-turbo (recommend: gpt-4-1106-preview)
- Implentation of the fakeopen openai api (free gpt4)
- If you don't want to use GPT set summary to 0, else 1

Example:

```ini
[moodle]
; Moodle URL for API access
moodleUrl = https://subdomain.example.com/
; Username and password for Moodle login
username = 123456
password = password
; API key for OpenAI and Pushbullet
openaikey = sk-xxxxx
pushbulletkey = o.xxxxx
; Activate or deactivate Pushbullet and Discord
pushbulletState = 0 ; 1: Activated, 0: Deactivated
webhookState = 1
; Discord webhook URL
webhookUrl = https://discord.com/api/webhooks/xxxxx/xxxxx
; System message for GPT-3 summarization
systemMessage = "YOUR SYSTEM PROMPT HERE, EXAMPLE IN config_example.ini"
; Set GPT model, standard gpt-3.5-turbo
model = gpt-3.5-turbo
; If fake open set to 1 then the bot uses the fakeopen api to generate the summary
fakeopen = 1
; If summary with GPT on set to 1, else 0
summary = 1
```

A example can be found in examples/example_config.ini

---

## <div id="usage">Usage</div>

Execute the script as follows:

```bash
python3 main.py
```

---

## <div id="Documentation">Documentation</div>

A documentation of the modules can be found in its respective folder.

---

## <div id="screenshots">Screenshots</div>

- Main Program
  <img src="assets/main.png" alt="Main Program" width="600"/>

- Discord Webhook
  <img src="assets/discord.jpg" alt="Discord Screenshot" width="600"/>

---

## <div id="Contributing">Contributing</div>

Contributions are always welcome! For bug reports, feature requests and questions, please submit an issue/PR.

---

## <div id="author">Author</div>

Made with ❤️ by [EvickaStudio](https://github.com/EvickaStudio).

---

## <div id="license">License</div>

This project is governed by the Apache 2.0 License - refer to the [LICENSE.md](LICENSE.md) file for further details.
