import os

IS_PRODUCTION = os.environ.get("PLATFORM_BRANCH") == "master"

# production settings
READTHEDOCS_NOTIFICATION_CHANNEL = "community_projects"
SLACK_TEAM_ID = os.environ.get("SLACK_TEAM_ID")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
SLACK_ADMIN_CHANNEL = os.environ.get("SLACK_ADMIN_CHANNEL", "")
SLACK_INTRODUCTION_CHANNEL = "introductions"

# Development settings
if not IS_PRODUCTION:
    READTHEDOCS_NOTIFICATION_CHANNEL = "general"
    SLACK_ADMIN_CHANNEL = "CJ1BWMBDX"  # general
    SLACK_INTRODUCTION_CHANNEL = "general"
