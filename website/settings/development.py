from ._base import *  # noqa

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

DEBUG = True

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
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'disabled': False,
            'propagate': True,
        }
    },
}

SECRET_KEY = 'PYSLACKERS_DEVELOPMENT_SECRET_KEY'
