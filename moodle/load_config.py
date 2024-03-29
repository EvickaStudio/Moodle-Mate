# Copyright 2024 EvickaStudio
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Config reader for moodle.py

Author: EvickaStudio
Data: 30.11.2023
Github: @EvickaStudio
"""

import configparser
import logging
import os
from functools import lru_cache


class Config:
    """
    A class to manage configuration settings for the application.
    ....
    """

    def __init__(self, config_file: str):
        """
        Initialize the Configuration class.
        ....
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

    @lru_cache(maxsize=None)
    def _cache_config_value(self, section: str, key: str) -> str | None:
        try:
            return self.config[section][key]
        except KeyError:
            logging.warning(
                f"Config key '{key}' not found in section '{section}'"
            )
            return None

    def get_config(self, section: str, key: str) -> str | None:
        """
        Retrieve a configuration value.
        ....
        """
        return self._config_cache(section, key)


# Example usage of the Configuration class
# config = Configuration("path_to_config_file.ini")
# value = config.get_config("section_name", "key_name")
