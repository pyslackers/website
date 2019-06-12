import os
import pathlib
import secrets

import dj_database_url
from celery.schedules import crontab
from platformshconfig import Config

config = Config()

ALLOWED_HOSTS = []

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
        'OPTIONS': {
            'min_length': 10,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]

BASE_DIR = pathlib.Path(__file__).parent.parent.parent


if config.is_valid_platform():
    redis_credentials = config.credentials('redis')

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': f"redis://{redis_credentials['host']}:{redis_credentials['port']}",
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL', 'redis://'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

CSRF_USE_SESSIONS = True

if config.is_valid_platform():
    DATABASES = {
        'default': dj_database_url.config(default=config.formatted_credentials('postgresql', 'postgresql_dsn')),  # noqa
    }
else:
    DATABASES = {
        'default': dj_database_url.config(default='postgres://postgres:@127.0.0.1:5432/postgres'),  # noqa
    }

DEBUG = False

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.sendgrid.net')

EMAIL_HOST_USER = os.getenv('EMAIL_USER')

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',

    'django_celery_beat',
    'raven.contrib.django.raven_compat',

    'app.core',
    'app.blog',
    'app.marketing',
    'app.slack',
]

LANGUAGE_CODE = 'en-us'

# https://docs.sentry.io/clients/python/integrations/django/#integration-with-logging  # noqa
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',  # noqa
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        # intercept any DisallowedHost errors before they can report to sentry
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

SITE_ID = 1

STATIC_ROOT = str(BASE_DIR / 'collected-static')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    str(BASE_DIR / 'app/static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(BASE_DIR / 'app/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

WSGI_APPLICATION = 'config.wsgi.application'

#################
# CELERY
#################

if config.is_valid_platform():
    redis_credentials = config.credentials('redis')
    BROKER_URL = f"redis://{redis_credentials['host']}:{redis_credentials['port']}"
    CELERY_RESULT_BACKEND = f"redis://{redis_credentials['host']}:{redis_credentials['port']}"
else:
    BROKER_URL = os.getenv('REDIS_URL', 'redis://')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', BROKER_URL)

CELERYBEAT_SCHEDULE = {
    'capture-snapshot-of-slack-users': {
        'task': 'app.slack.tasks.capture_snapshot_of_user_count',
        'schedule': crontab(minute=0, hour=0),
    },
    'refresh-burner-domain-cache': {
        'task': 'app.marketing.tasks.refresh_burner_domain_cache',
        'schedule': crontab(minute=0, hour=23, day_of_week=0),
    },
    'refresh-github-project-cache': {
        'task': 'app.marketing.tasks.update_github_project_cache',
        'args': ('pyslackers',),
        'schedule': crontab(minute=0, hour=23),
    },
}

CELERYBEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

#################
# CUSTOM
#################

SLACK_JOIN_CHANNELS = os.getenv('SLACK_JOIN_CHANNELS', '').split(',')

SLACK_OAUTH_TOKEN = os.getenv('SLACK_OAUTH_TOKEN')
