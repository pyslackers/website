import raven

from ._base import *  # noqa
from platformshconfig import Config

config = Config()

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    '.pyslackers.com',
    '*.platformsh.site'
]

CSRF_COOKIE_SECURE = True

DEBUG = False

if "SENTRY_DSN" in os.environ:
    RAVEN_CONFIG = {
        'dsn': os.environ["SENTRY_DSN"],  # noqa
        'release': config.treeID,  # noqa
    }

SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'
