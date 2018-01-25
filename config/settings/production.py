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

RAVEN_CONFIG = {
    'dsn': f'https://94925f1b36294c9eb5e71aa8b7251cb8:{os.environ.get("RAVEN_PASSWORD", "")}@sentry.io/269271',  # noqa
    'release': raven.fetch_git_sha(str(BASE_DIR)),  # noqa
    'ignore_exceptions': [
        'django.security.DisallowedHost'
    ]
}

SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'
