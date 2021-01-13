import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgres://127.0.0.1:5432/postgres")

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

SENTRY_DSN = os.getenv("SENTRY_DSN")

SENTRY_ENVIRONMENT = os.getenv("PLATFORM_BRANCH")

SENTRY_RELEASE = os.getenv("PLATFORM_TREE_ID")

IS_PRODUCTION = os.getenv("PLATFORM_BRANCH") == "master"

# This must be an admin user's token on the team
SLACK_INVITE_TOKEN = os.getenv("SLACK_INVITE_TOKEN", os.getenv("SLACK_OAUTH_TOKEN"))

SLACK_TOKEN = os.getenv("SLACK_TOKEN", os.getenv("SLACK_OAUTH_TOKEN"))

# We are running on platform.sh
if "PLATFORM_RELATIONSHIPS" in os.environ:
    REDIS_URL = "redis://applicationcache.internal:6379/0"
    DATABASE_URL = "postgresql://main:main@database.internal:5432/main"
