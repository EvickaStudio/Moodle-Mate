# Moodle Mate

<div>
  <img src="assets/moodlematev_gh_preview.png" alt="Moodle Mate logo hero image with an orange background" title="Hero">
  <h1>Moodle Mate</h1>
  <p><strong>Your Smart Moodle Notification Assistant</strong></p>
</div>

<p>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/actions"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/EvickaStudio/Moodle-Mate/ci.yml?+label=Build%20Status"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/blob/main/LICENSE.md"><img alt="GitHub license" src="https://img.shields.io/github/license/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/commits"><img alt="Commits" src="https://img.shields.io/github/commit-activity/m/EvickaStudio/Moodle-Mate?label=commits"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/pulls"><img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/EvickaStudio/Moodle-Mate"></a>
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/EvickaStudio/Moodle-Mate">
  <a href="https://deepwiki.com/EvickaStudio/Moodle-Mate"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

## What is Moodle Mate?

Moodle Mate is a Python application that fetches notifications from a Moodle instance (e.g. a school or university) and
delivers them to a notification platform (e.g. Discord). This allows you to stay up to date with your courses and
activities without manually checking your email or Moodle.

Moodle Mate includes an optional AI-powered summarization feature that summarizes notifications and adds a short TL;DR.
BYOK (Bring Your Own Key): you can use any AI provider that supports an OpenAI-compatible API. If you have privacy
concerns, you can use a locally hosted model (e.g. with
[Ollama](https://ollama.com/) or other tools like LMStudio, vLLM etc. that have OpenAI-compatible APIs).

## Key Features

- **Notification Management**
  - Automatically fetches and processes notifications from Moodle, and saves current state on shutdown.
  - Optional AI-based summarization creates quick TL;DRs for easier review.
  - Converts HTML notifications to Markdown for improved readability using [turndown-python](https://github.com/EvickaStudio/turndown-python) for notification
  providers that do not support HTML.

- **Web Dashboard (Optional, currently in beta)**
  - Monitor system status, logs, and configuration.
  - Planned live configuration editing for some settings.
  - Send test notifications.
  - Protected by optional authentication.

- **Multi-Platform Support**
  - Discord (via webhooks)
  - Pushbullet (send to all your devices)
  - Plugin system for custom notification providers
  - Modular architecture for easy integration of new platforms

- **AI Integration**
  - Support for multiple OpenAI-API-compatible providers.
  - Configurable models and parameters
  - Optional summarization feature

## Requirements

- Python 3.11 or higher
- Internet connection (when your Moodle server or AI provider is not locally hosted)
- Moodle instance with REST API access enabled (this is not enabled by default)

## Installation

### Option 1: Standard Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/EvickaStudio/Moodle-Mate.git
   cd Moodle-Mate
   ```

2. **Install Dependencies**

   Recommended (uv):

   ```bash
   uv sync --extra dev
   ```

   Optional (Make shortcuts):

   ```bash
   make install
   make run
   make test
   make help
   ```

   If you prefer a virtualenv:

   ```bash
   python -m venv venv
   source venv/bin/activate
   # source venv/bin/activate.fish for fish shell
   pip install -r requirements.txt
   ```

3. **Configure the Application**

   Create a `.env` file in the root directory. You can copy the example:

   ```bash
   cp example.env .env
   ```

   Edit `.env` with your settings. Configuration uses environment variables with the `MOODLEMATE_` prefix.

### Option 2: Docker Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/EvickaStudio/Moodle-Mate.git
   cd Moodle-Mate
   ```

2. **Configuration**

   Create and edit your `.env` file:

   ```bash
   cp example.env .env
   # Edit .env with your settings
   ```

3. **Build and Run with Docker**

   ```bash
   # Build the Docker image
   docker compose build

   # Run the container
   docker compose up -d
   ```

4. **View Logs**

   ```bash
   docker compose logs -f
   ```

## Usage

### Standard Usage

To start Moodle Mate, run:

```bash
uv run moodlemate
```

### Docker Usage

When using Docker, the application starts automatically when you run:

```bash
docker compose up -d
```

To stop the application:

```bash
docker compose down
```

When running, the application will:

1. Validate your configuration.
2. Start the Web Dashboard if enabled (default: <http://localhost:9095>).
3. Connect to your Moodle instance.
4. Continuously monitor for new notifications.
5. Process and deliver notifications according to your settings.

## Web Dashboard

Moodle Mate includes a built-in web dashboard for monitoring and configuration.

- **URL**: `http://127.0.0.1:9095` (default)
- **Features**:
  - View current status and metrics.
  - Trigger test notifications.
  - Edit non-sensitive configuration live (Web UI auth required).

**Security**: `MOODLEMATE_WEB__AUTH_SECRET` is required when Web UI is enabled. The dashboard always requires login and sets secure session/CSRF cookies.

## Screenshots

*Colors differ across screenshots because different Termius themes were used.*

> Versions are slightly mixed up, sorry.

### v2.0.3 (Web UI)

![v2.2.1](assets/webui_v2.0.3.png)

### v2.0.2 (Docker)

![v2.0.2](assets/running_v2.0.2.png)

Running as Docker daemon, to see the logs run `docker compose logs -f`

### v2.0.1

![v2.0.1](assets/running_v2.0.1.webp)

When running as a standard Python application, logs appear in the terminal where you start the command. For KVM setups
running Moodle Mate in the background, Docker is recommended, but you can also use tmux, screen, or tmuxinator.

## Documentation

See the Diataxis-based docs index at `docs/README.md`.

### Discord notification

![v2.0.2](assets/preview.png)

## Creating Custom Notification Providers

MoodleMate now supports a plugin system that allows you to easily create and add your own notification providers without modifying the core code.

### Quick Start

1. Start from the template at `src/moodlemate/templates/notification_service_template.py`.
2. Copy it to `src/moodlemate/providers/notification/your_service_name/provider.py` and rename the class (e.g., `YourServiceNameProvider`).
3. Implement `send(self, subject, message, summary=None) -> bool` with your service’s API.
4. Add configuration to your `.env` file:

   ```env
   MOODLEMATE_YOUR_SERVICE_NAME__ENABLED=true
   MOODLEMATE_YOUR_SERVICE_NAME__API_KEY=your_key
   ```

5. Optionally verify with `uv run moodlemate --test-notification`.

See detailed steps in [How to add a custom notification provider](docs/how-to/add-custom-provider.md).

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Moodle Mate is licensed under the Apache License 2.0. See [LICENSE.md](LICENSE.md) for more details.

## Author

Created with ❤️ by [EvickaStudio](https://github.com/EvickaStudio)
