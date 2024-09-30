import configparser
import logging
import os
from functools import lru_cache
from typing import Optional


class Config:
    """
    A class to manage configuration settings for the application.
    """

    def __init__(self, config_file: str):
        """
        Initialize the Config class.
        """
        self.config = configparser.ConfigParser()
        self._config_cache = lru_cache(maxsize=None)(self._cache_config_value)

        # Validate the existence of the config file
        try:
            self.config.read(self._get_absolute_path(config_file))
        except (FileNotFoundError, configparser.Error) as e:
            logging.error(f"Error reading config file: {str(e)}")

    @staticmethod
    def _get_absolute_path(path: str) -> str:
        return os.path.abspath(os.path.expanduser(path))

    def _cache_config_value(self, section: str, key: str) -> Optional[str]:
        try:
            return self.config[section][key]
        except KeyError:
            logging.warning(
                f"Config key '{key}' not found in section '{section}'"
            )
            return None

    def get_config(self, section: str, key: str) -> Optional[str]:
        """
        Retrieve a configuration value.
        """
        return self._config_cache(section, key)
