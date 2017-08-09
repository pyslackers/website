from .base import *  # noqa

CACHES['default']['OPTIONS'] = {  # noqa
    'REDIS_CLIENT_CLASS': 'fakeredis.FakeStrictRedis',
}

CELERY_ALWAYS_EAGER = True

SECRET_KEY = 'PYSLACKERS_TESTING_SECRET_KEY'
