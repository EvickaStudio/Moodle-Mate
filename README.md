<div align="center">
  <img src="assets/logo.png" alt="Logo" width="200"/>
  <h1>Moodle Mate</h1>
  <p><strong>Automated Moodle Notification Summarization</strong></p>
</div>

---

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

---

## <div id="overview">Overview</div>

Moodle Mate is an advanced Python application designed to streamline the process of receiving Moodle notifications. It fetches notifications from Moodle, summarizes them using GPT-3 or GPT-4 and sends them to the user via Pushbullet and Discord. The application is designed to run on a server and can be configured to run at specific intervals.

Utilizes GPT-3.5-turbo for cost-effective operations (under 15 cents/month, excluding server costs).
Alternatively you could just disable summarization in the config file and use the script without GPT-3/4.

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

<img src="assets/discord.jpg" alt="Discord Screenshot" width="600"/>

---

## <div id="Contributing">Contributing</div>

Contributions are always welcome! For bug reports, feature requests and questions, please submit an issue/PR.

---

## <div id="author">Author</div>

Made with ❤️ by [EvickaStudio](https://github.com/EvickaStudio).

---

## Notes

I'm currently in the process of rewriting the codebase to make it more modular and easier to maintain. The current codebase is a mess and I'm sorry for that. Thus, the code might be a bit messy and not up to my 
standards in the main file...
Also the CUI version is currently not updates and thus
removed, but will be added again in the future.
Old code can be found in old version folder.