# Moodle Integration Modules

## Overview
This directory contains modules for integrating with Moodle, a popular learning management system. The primary focus is on interacting with Moodle's API to fetch information and notifications.

### Modules
- [Moodle API Wrapper](#moodle-api-wrapper)

## [Moodle API Wrapper](api.py)
The `MoodleAPI` module is a Python wrapper for interacting with the Moodle API. It simplifies the process of making requests to the Moodle server, handling user authentication, and fetching various types of data from Moodle.

### Usage
To use the Moodle API module:
1. Initialize the `MoodleAPI` class with a configuration object.
2. Use the provided methods to interact with the Moodle API.

Example:
```python
from api import MoodleAPI
from load_config import Config

config = Config("config.ini")
moodle_api = MoodleAPI(config)

username = config.get_config("moodle", "username")
password = config.get_config("moodle", "password")

moodle_api.login(username, password)
site_info = moodle_api.get_site_info()
print(site_info)
```

### Features
- User authentication with Moodle.
- Fetching site information.
- Retrieving user-specific notifications.
- Extensible structure for adding more Moodle API endpoints.

## Extending the Moodle Integration
To extend the Moodle integration:
1. Add new methods to the `MoodleAPI` class for additional API endpoints.
2. Ensure that the endpoints are enabled or you have the appropriate permissions to access them.