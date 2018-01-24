import os

from ._base import *  # noqa


CACHES['default']['LOCATION'] = os.getenv('REDIS_URL', 'redis://localhost:6379/1')  # noqa

BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')

CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', BROKER_URL)

RATELIMIT_CACHE_PREFIX = 'rl:test:'

SECRET_KEY = 'PYSLACKERS_TESTING_SECRET_KEY'
