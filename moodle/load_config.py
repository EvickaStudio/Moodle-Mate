"""
Config reader for moodle.py

Author: EvickaStudio
Data: 30.11.2023
Github: @EvickaStudio
"""

import configparser
import logging
import os


class Config:
    """
    A class to manage configuration settings for the application.

    This class handles reading from a configuration file and provides
    a method to retrieve specific configuration values. It includes error handling
    for non-existent files and parsing errors. Additionally, it implements caching
    to optimize performance by avoiding redundant file reads.

    Attributes:
        config (ConfigParser): An instance of ConfigParser to read config files.
        _config_cache (dict): A cache to store and retrieve configuration values.
    """

    def __init__(self, config_file: str):
        """
        Initialize the Config class.

        Args:
            config_file (str): The path to the configuration file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        self.config = configparser.ConfigParser()
        self._config_cache = {}

        # Validate the existence of the config file
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")

        # Read the configuration file and handle parsing errors
        try:
            self.config.read(config_file)
        except configparser.Error as e:
            logging.error(f"Error reading config file: {e}")

    def get_config(self, section: str, key: str) -> str:
        """
        Retrieve a configuration value.

        Args:
            section (str): The section of the configuration.
            key (str): The key within the section to retrieve.

        Returns:
            str: The configuration value. If the key or section is not found,
                 None is returned.
        """
        # Check if the value is cached
        if (section, key) in self._config_cache:
            return self._config_cache[(section, key)]

        # Retrieve and cache the configuration value, handling missing keys or sections
        try:
            value = self.config[section][key]
            self._config_cache[(section, key)] = value
            return value
        except KeyError:
            logging.warning(f"Config key '{key}' not found in section '{section}'")
            return None


# Example usage of the Config class
# config = Config("path_to_config_file.ini")
# value = config.get_config("section_name", "key_name")
