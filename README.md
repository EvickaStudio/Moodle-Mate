# Moodle Mate

<div align="center">
  <img src="assets/moodlematev_gh_preview.png" alt="Moodle Mate Logo">
  <h1>Moodle Mate</h1>
  <p><strong>Your Smart Moodle Notification Assistant</strong></p>
</div>

<p align="center">
  <a href="https://github.com/EvickaStudio/Moodle-Mate/actions"><img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/EvickaStudio/Moodle-Mate/ci.yml?+label=Build%20Status"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/blob/main/LICENSE.md"><img alt="GitHub license" src="https://img.shields.io/github/license/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/commits"><img alt="Commits" src="https://img.shields.io/github/commit-activity/m/EvickaStudio/Moodle-Mate?label=commits"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/EvickaStudio/Moodle-Mate"></a>
  <a href="https://github.com/EvickaStudio/Moodle-Mate/pulls"><img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/EvickaStudio/Moodle-Mate"></a>
  <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/EvickaStudio/Moodle-Mate">
  <a href="https://deepwiki.com/EvickaStudio/Moodle-Mate"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
</p>

## What is Moodle Mate?

Moodle Mate is an Python application that fetches notifications from a Moodle instance (eg. a school or university) and delivers them to a notification platform (eg. Discord). This will allow you to stay up to date with all your courses and activities without having to manually check your E-Mail or Moodle.

Moodle Mate comes with an optional AI-powered summarization feature that will summarize the notifications for you and add it as an small TLDR to the notification. BYOK - Bring your own key, you can use any AI provider you want that supports the openai api structure, so if you have privacy concerns you can use an local hosted model (e.g. with [Ollama](https://ollama.ai/)).

## Key Features

- **Modern Web Interface** 🌐
  - Beautiful, responsive dashboard built with TailwindCSS and Maybe design system
  - Real-time monitoring and configuration management
  - Dark/light theme support with accessible design
  - Mobile-friendly interface for on-the-go management

- **Smart Notification Management**
  - Automatically fetch and process notifications from Moodle.
  - Optional AI-based content summarization that creates quick TLDRs.
  - Converts HTML notifications to Markdown for improved readability using [turndown-python](https://github.com/EvickaStudio/turndown-python).

- **Multi-Platform Support**
  - Discord (via webhooks)
  - Pushbullet (send to all your devices)
  - Plugin system for custom notification providers
  - Modular architecture for easy integration of new platforms

- **AI Integration**
  - Support for multiple AI providers (OpenAI API like)
  - Configurable models and parameters
  - Optional summarization feature

## Requirements

- Python 3.10 or higher
- Internet connection
- Moodle instance with REST API access enabled

## Installation

### Option 1: Standard Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/EvickaStudio/Moodle-Mate.git
   cd Moodle-Mate
   ```

2. **Install Dependencies**

   You can optionally use a virtual environment to install the dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   # soure venv/bin/activate.fish for fish shell
   ```

   Then install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Application**

   The recommended way is to use the config generator:

   ```bash
   python main.py --gen-config
   ```

   Alternatively, you can manually edit the `config.example.ini` file:

   ```bash
   cp config.example.ini config.ini
   # Edit config.ini with your settings
   ```

   Ensure your config.ini settings align with the latest [Configuration documentation](src/core/config/README.md), as example_config.ini may be more recent.

### Option 2: Docker Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/EvickaStudio/Moodle-Mate.git
   cd Moodle-Mate
   ```

2. **Configuration**

   First, generate a configuration file:

   ```bash
   # Using Python directly
   python main.py --gen-config
   
   # Or using Docker (this will install required dependencies first)
   docker run --rm -it -v $(pwd):/app python:3.12-slim-bookworm bash -c "pip install -r /app/requirements.txt && python /app/main.py --gen-config"
   ```

   Alternatively, you can manually edit the `config.example.ini` file:

   ```bash
   cp config.example.ini config.ini
   # Edit config.ini with your settings
   ```

   For more information on the configuration, see the [Configuration](src/core/config/README.md) documentation. (might be not up to date with example_config.ini)

3. **Edit the Configuration**

   Edit the generated `config.ini` file with your settings.

4. **Build and Run with Docker**

   ```bash
   # Build the Docker image
   docker compose build
   
   # Run the container
   docker compose up -d
   ```

5. **View Logs**

   ```bash
   docker compose logs -f
   ```

## Usage

### Standard Usage

To start Moodle Mate, simply run:

```bash
python main.py
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

### Web Interface Usage

For a modern, user-friendly experience, you can use the web interface:

#### Quick Start
```bash
# Start the web interface (default: http://localhost:5000)
python web_launcher.py

# Custom host and port
python web_launcher.py --host 0.0.0.0 --port 8080

# Debug mode for development
python web_launcher.py --debug
```

The web interface includes:
- **Dashboard**: Overview of system status and recent notifications
- **Notifications**: History and management of Moodle notifications
- **Configuration**: User-friendly settings management
- **Health**: System monitoring and diagnostics
- **Dark/Light Theme**: Toggle between themes with persistent preference

The web interface provides:
- 📊 **Real-time dashboard** with system status and recent notifications
- ⚙️ **Interactive configuration** forms for all settings
- 📋 **Notification history** with search and filtering
- 🏥 **Health monitoring** with detailed system metrics
- 🎨 **Modern UI** with dark/light theme support

Visit the [Web Interface Documentation](src/ui/web/README.md) for more details.

When running, the application will:

1. Validate your configuration.
2. Connect to your Moodle instance.
3. Continuously monitor for new notifications.
4. Process and deliver notifications according to your settings.

## Screenshots

*Colors between the screenshots are different because of different themes in Termius.*

### v2.0.2 (Docker)

![v2.0.2](assets/running_v2.0.2.png)

Running as Docker daemon, to see the logs run `docker compose logs -f`

### v2.0.1

![v2.0.1](assets/running_v2.0.1.webp)

Running as standard python application, you will automatically see the logs in the terminal you ran the command in. For KVMs running MoodleMate in the background, docker is the recommended way to run it, but you can also use tmux, screen or tmuxinator to run it in the background.

### Discord notification

![v2.0.2](assets/preview.png)

## Creating Custom Notification Providers

MoodleMate now supports a plugin system that allows you to easily create and add your own notification providers without modifying the core code.

### Quick Start

1. Copy the template from `src/templates/notification_service_template.py` to `src/providers/notification/your_service_name/provider.py`
2. Rename the class to match your service (e.g., `YourServiceNameProvider`)
3. Implement the `send()` method with your service's API
4. Add your service's configuration to `config.ini`

For more detailed information, see the [Creating Custom Notification Providers](docs/CUSTOM_PROVIDERS.md) documentation.

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
