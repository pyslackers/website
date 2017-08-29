import os
import sys

from celery import Celery

if any(x in sys.argv for x in ['./manage.py', 'manage.py']):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'config.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'config.settings.production')

app = Celery('config')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks()
