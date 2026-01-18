from moodlemate.config import Settings
from moodlemate.moodle.api import MoodleAPI

# Create a Settings object (loads from .env)
settings = Settings()

# Initialize MoodleAPI with settings
api = MoodleAPI(
    url=settings.moodle.url,
    username=settings.moodle.username,
    password=settings.moodle.password,
)

# Login using credentials from settings
api.login()

# Get site information
site_info = api.get_site_info()
print(site_info)
