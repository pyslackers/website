import os
import pathlib
import secrets

import dj_database_url
from celery.schedules import crontab


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

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

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
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',

    'django_celery_beat',

    'app.core',
    'app.blog',
    'app.marketing',
    'app.slack',
]

LANGUAGE_CODE = 'en-us'

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
# ALLAUTH
#################

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

ACCOUNT_EMAIL_REQUIRED = True

ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

ACCOUNT_LOGOUT_REDIRECT_URL = '/'

ACCOUNT_PRESERVE_USERNAME_CASING = False

ACCOUNT_USERNAME_BLACKLIST = [
    'me', 'admin', 'administrator', 'sudo', 'root',
]

ACCOUNT_USERNAME_MIN_LENGTH = 5

LOGIN_REDIRECT_URL = '/'

SOCIALACCOUNT_EMAIL_VERIFICATION = False

SOCIALACCOUNT_EMAIL_REQUIRED = False

SOCIALACCOUNT_QUERY_EMAIL = False

SOCIALACCOUNT_STORE_TOKENS = False  # we are just using them for auth.

#################
# CELERY
#################

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
