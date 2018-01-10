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

LOGGING = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': "[PYSLACKERSWEB] [%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",  # noqa
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'verbose': {
            'format': '%(process)-5d %(thread)d %(name)-50s %(levelname)-8s %(message)s',  # noqa
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'syslog': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'standard',
            'facility': 'user',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'syslog'],
            'level': 'INFO',
            'disabled': False,
            'propagate': True,
        }
    },
}

RAVEN_CONFIG = {
    'dsn': f'https://94925f1b36294c9eb5e71aa8b7251cb8:{os.environ.get("RAVEN_PASSWORD", "")}@sentry.io/269271',  # noqa
    'release': raven.fetch_git_sha(str(BASE_DIR)),  # noqa
}

SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'
