from ._base import *  # noqa


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CELERY_ALWAYS_EAGER = True

SECRET_KEY = 'PYSLACKERS_TESTING_SECRET_KEY'

############
# RATE LIMIT
############

RATELIMIT_CACHE_PREFIX = 'rl:test:'
