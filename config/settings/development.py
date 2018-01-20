from ._base import *  # noqa


CELERY_ALWAYS_EAGER = False

DEBUG = True

INSTALLED_APPS += [  # noqa
    'debug_toolbar',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

MIDDLEWARE.insert(3, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa

RATELIMIT_ENABLE = False

SECRET_KEY = 'PYSLACKERS_DEVELOPMENT_SECRET_KEY'
