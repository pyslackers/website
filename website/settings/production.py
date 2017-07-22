from ._base import *  # noqa

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

SESSION_COOKIE_SECURE = True

X_FRAME_OPTIONS = 'DENY'
