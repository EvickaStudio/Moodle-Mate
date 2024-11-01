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

# Testing script for MoodleAPI


from moodle.api import MoodleAPI
from utils.load_config import Config

config = Config("config.ini")  # Create a Config object
api = MoodleAPI(config)  # Pass the Config object to MoodleAPI
username = config.get_config("moodle", "username")
password = config.get_config("moodle", "password")

api.login(username, password)
site_info = api.get_site_info()
print(site_info)

# Works for me...
