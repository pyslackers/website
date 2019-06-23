import os


REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

SENTRY_DSN = os.getenv("SENTRY_DSN")

SENTRY_ENVIRONMENT = os.getenv("PLATFORM_BRANCH")

SENTRY_RELEASE = os.getenv("PLATFORM_TREE_ID")

# This must be an admin user's token on the team
SLACK_INVITE_TOKEN = os.getenv("SLACK_INVITE_TOKEN", os.getenv("SLACK_OAUTH_TOKEN"))

SLACK_TOKEN = os.getenv("SLACK_TOKEN", os.getenv("SLACK_OAUTH_TOKEN"))
