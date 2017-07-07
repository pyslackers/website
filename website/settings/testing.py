from ._base import *  # noqa

ALLOWED_HOSTS = []

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'REDIS_CLIENT_CLASS': 'fakeredis.FakeStrictRedis',
        }
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': 5432,
    }
}

DEBUG = True

SECRET_KEY = 'PYSLACKERS_TESTING_SECRET_KEY'
