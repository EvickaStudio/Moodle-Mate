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
  <img src="assets/logo.svg" style="width: 160px;">
  <h1>Moodle Mate</h1>
  <p><strong>Automated Moodle Notification Summarization</strong></p>
</div>

---

<p align="center">
  <a href="https://github.com/EvickaStudio/Moodle-Mate/actions"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/EvickaStudio/Moodle-Mate/ci.yml?+label=Build%20Status"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/blob/main/LICENSE.md"><img alt="GitHub license" src="https://img.shields.io/github/license/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/pulls"><img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/EvickaStudio/Moodle-Mate"></a>
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/EvickaStudio/Moodle-Mate">
  <a href="https://github.com/EvickaStudio/Moodle-Mate/watchers"><img alt="GitHub Watchers" src="https://img.shields.io/github/watchers/EvickaStudio/Moodle-Mate?style=flat&logo=github"></a>
  <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/EvickaStudio/Moodle-Mate">

> [!NOTE]
> The codebase is currently under refinement for enhanced modularity and maintainability. For the latest version, please visit the [`dev`](https://github.com/EvickaStudio/Moodle-Mate/tree/dev) branch.

---

## Table of Contents

---

1. [Overview](#overview)
2. [Dependencies](#dependencies)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Documentation](#documentation)
7. [Screenshots](#screenshots)
8. [Contributing](#contributing)
9. [Author](#author)
10. [License](#license)

## <div id="overview">Overview</div>

---

Moodle Mate is an automated notification summarization tool for Moodle, which retrieves notifications from your Moodle account, summarizes their content using powerful AI models like GPT-3 or GPT-4 (optional), and delivers the exctracted information directly to you through channels such as Pushbullet and Discord. Designed for seamless integration into server environments, Moodle Mate offers high flexibility with adjustable update intervals tailored to meet your needs.

**Key Features:**

- Cost-effective operation with GPT-3.5-turbo, minimizing expenses. (typically less than $0.15 per month, excluding server expenses). Alternatively you could just disable summarization in the config file
- Optional OpenAI Assistant integration for intelligent, context-aware responses, currently available in German. To use the Assistant, set the `test` variable in `summarizer.summarize` to `True`:

  Example:

  ```python
  # utils > main_loop.py > main_loop()

  # line 56, works [08.01.2024]
  summary = summarizer.summarize(text, True)
  ```

- Supports popular platforms including Pushbullet, Discord, and NTFY (BETA) for versatile notification delivery.
- Offers flexible scheduling for periodic background execution and incorporates error handling mechanisms.

**NEW**: Experimentation with fakeopen, a free API for GPT-4-32k chat completions. (Usage discretion advised due to potential inconsistencies.)

## <div id="dependencies">Dependencies</div>

---

Moodle Mate depends on several specialized API wrappers and libraries:

- **MoodleAPI**: A custom interface for Moodle API interactions.
- **OpenAI**: Integration with OpenAI's API.
- **Pushbullet**: Connectivity with Pushbullet API.
- **NTFY**: Connectivity with NTFY API.
- **Discord**: Implementation using Discord webhooks.

To ensure smooth operation of Moodle Mate, ensure Python 3.10 or higher is installed.

- **Python >= 3.10:** Necessary for compatibility and functionality.

## <div id="installation">Installation</div>

---

To install Moodle Mate, follow these steps:

1. Clone the repository and access the main directory:
   ```bash
   git clone https://github.com/EvickaStudio/Moodle-Mate.git
   cd Moodle-Mate
   ```
2. Install necessary Python dependencies from the _requirements.txt_ file:
   ```bash
   pip install -r requirements.txt
   ```

## <div id="configuration">Configuration</div>

---

Configuration of Moodle Mate requires setting up a `config.ini` file. Key parameters include Moodle URL, account credentials, and various API keys for functionality and integrations.

| Parameter       | Description                               | Required | Default            |
| --------------- | ----------------------------------------- | -------- | ------------------ |
| moodleUrl       | Moodle URL for API access                 | Yes      | N/A                |
| username        | Moodle Account Username                   | Yes      | N/A                |
| password        | Moodle Account Password                   | Yes      | N/A                |
| openaikey       | OpenAI API Key                            | No       | N/A                |
| pushbulletkey   | Pushbullet API Key                        | No       | N/A                |
| pushbulletState | Pushbullet State (ON = 1 else 0)          | No       | 0                  |
| webhookState    | Webhook State (ON = 1 else 0)             | No       | 0                  |
| webhookUrl      | Discord Webhook URL                       | Yes      | N/A                |
| systemMessage   | System Message for GPTs                   | Yes      | default config     |
| model           | GPT Model (recommend: gpt-4-1106-preview) | No       | gpt-3.5-turbo-1106 |
| fakeopen        | Implementation of fakeopen API            | Yes      | 0                  |
| summary         | Use GPT for summary (ON = 1 else 0)       | Yes      | 0                  |

A detailed example configuration is available [here](example/example_config.ini).

## <div id="usage">Usage</div>

---

With the configuration complete, execute the main script to start the application:

> [!TIP]
> Moodle Mate processes only new notifications, current last notification will not be send.

```bash
python3 main.py
```

## <div id="Documentation">Documentation</div>

---

Comprehensive documentation, detailing functionalities and operational guidelines, is organized by module within each directory.

## <div id="screenshots">Screenshots</div>

---

Screenshots of the application in action:

- Main Program Interface
  <img src="assets/main.png" alt="Main Program" width="600"/>

- Discord Webhook Integration
  <img src="assets/discord.jpg" alt="Discord Screenshot" width="600"/>

## <div id="Contributing">Contributing</div>

---

Contributions to Moodle Mate are welcomed. We encourage reporting of bugs, feature suggestions, and general inquiries through issues or PR.

## <div id="author">Author</div>

---

Made with ❤️ by [EvickaStudio](https://github.com/EvickaStudio). Reach out if you encounter any challenges or need assistance.

## <div id="license">License</div>

---

Moodle Mate is distributed under the Apache License 2.0. For complete licensing details, please refer to the [LICENSE.md](LICENSE.md) file.
