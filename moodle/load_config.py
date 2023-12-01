"""
Config reader for moodle.py

Author: EvickaStudio
Data: 30.11.2023
Github: @EvickaStudio
"""

import configparser
import logging


class Config:
    def __init__(self, config_file: str):
        self.config = configparser.ConfigParser()
        try:
            self.config.read(config_file)
        except configparser.Error as e:
            logging.error(f"Error reading config file: {e}")

    def get_config(self, section: str, key: str) -> str:
        try:
            return self.config[section][key]
        except KeyError:
            logging.error(f"Config key '{key}' not found in section '{section}'")
            return None
