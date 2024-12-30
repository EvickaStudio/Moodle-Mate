# Moodle Mate

<div align="center">
  <img src="assets/logo.svg" alt="Moodle Mate Logo" width="160">
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
</p>

## Overview

Moodle Mate is a modern Python application that enhances your Moodle experience by automatically managing and delivering notifications. It features AI-powered summarization, multi-platform notification delivery, and efficient resource management.

## Key Features

- **Smart Notification Management**
  - Automatic notification fetching and processing
  - AI-powered content summarization (optional)
  - HTML to Markdown conversion for better readability
  - Configurable update intervals

- **Multi-Platform Support**
  - Discord (via webhooks)
  - Support for additional notification platforms
  - Extensible architecture for custom integrations

- **Advanced Integration**
  - Global request session management
  - Consistent headers and User-Agent across all requests
  - Connection pooling for improved performance
  - Automatic retry mechanism for failed operations

- **Resource Efficient**
  - Low memory footprint (~50MB RAM)
  - Optimized for long-running operations
  - Suitable for resource-constrained environments (e.g., Raspberry Pi)

- **AI Integration**
  - Support for multiple AI providers
  - Configurable models and parameters
  - Cost-effective operation (~$0.10/month for typical usage)
  - Optional summarization feature

## Requirements

- Python 3.10 or higher
- Internet connection
- Moodle instance with API access

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/EvickaStudio/Moodle-Mate.git
   cd Moodle-Mate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Application**
   ```bash
   cp config.example.ini config.ini
   # Edit config.ini with your settings
   ```

## Configuration

The `config.ini` file controls all aspects of Moodle Mate. Here are the key sections:

### Moodle Settings
```ini
[moodle]
url = https://your.moodle.instance
username = your_username
password = your_password
```

### AI Settings
```ini
[ai]
enabled = 1
api_key = your_api_key
model = gpt-4
temperature = 0.7
max_tokens = 150
endpoint = https://api.openai.com/v1  # Optional custom endpoint
```

### Notification Settings
```ini
[notification]
max_retries = 3
fetch_interval = 300  # seconds
```

### Discord Settings
```ini
[discord]
enabled = 1
webhook_url = your_webhook_url
bot_name = MoodleMate
thumbnail_url = your_thumbnail_url
```

## Usage

Start the application:
```bash
python main.py
```

The application will:
1. Validate your configuration
2. Connect to your Moodle instance
3. Start monitoring for new notifications
4. Process and deliver notifications according to your settings

## Development

The project follows modern Python best practices:
- Type hints for better code quality
- Comprehensive logging
- Unit tests
- Modular architecture

Key components:
- `src/moodle/`: Moodle API integration
- `src/notification/`: Notification processing and delivery
- `src/utils/`: Shared utilities and helpers
- `src/gpt/`: AI integration

## Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Apache License 2.0 - See [LICENSE.md](LICENSE.md) for details.

## Author

Created with ❤️ by [EvickaStudio](https://github.com/EvickaStudio)

---

<div align="center">
  <img src="assets/preview.png" alt="Discord Integration Preview" width="600">
</div>
