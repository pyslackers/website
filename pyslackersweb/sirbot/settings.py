import os

# production
READTHEDOCS_NOTIFICATION_CHANNEL = "community_projects"

# Development
if os.environ.get("PLATFORM_BRANCH") != "main":
    READTHEDOCS_NOTIFICATION_CHANNEL = "general"
