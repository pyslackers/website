from ._base import *  # noqa


CACHES['default']['LOCATION'] = 'redis://localhost:6379/1'  # noqa

CELERY_ALWAYS_EAGER = True

SECRET_KEY = 'PYSLACKERS_TESTING_SECRET_KEY'

############
# RATE LIMIT
############

RATELIMIT_CACHE_PREFIX = 'rl:test:'
