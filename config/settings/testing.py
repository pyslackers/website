from ._base import *  # noqa


CELERY_ALWAYS_EAGER = True

SECRET_KEY = 'PYSLACKERS_TESTING_SECRET_KEY'

############
# RATE LIMIT
############

RATELIMIT_CACHE_PREFIX = 'rl:test:'
