# Testing script for MoodleAPI


from moodle.api import MoodleAPI
from moodle.load_config import Config

config = Config("config.ini")  # Create a Config object
api = MoodleAPI(config)  # Pass the Config object to MoodleAPI
username = config.get_config("moodle", "username")
password = config.get_config("moodle", "password")

api.login(username, password)
site_info = api.get_site_info()
print(site_info)

# Works for me...
