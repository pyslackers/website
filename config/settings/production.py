import raven

from ._base import *  # noqa


ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    '.pyslackers.com',
]

CSRF_COOKIE_SECURE = True

DEBUG = False

if "SENTRY_DSN" in os.environ:
    RAVEN_CONFIG = {
        'dsn': os.environ["SENTRY_DSN"],  # noqa
        'release': raven.fetch_git_sha(str(BASE_DIR)),  # noqa
    }

SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'
