import os

# production
READTHEDOCS_NOTIFICATION_CHANNEL = "community_projects"

# Development
if os.environ.get("PLATFORM_BRANCH") != "master":
    READTHEDOCS_NOTIFICATION_CHANNEL = "general"
