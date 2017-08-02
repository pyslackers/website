import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

app = Celery('website')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks()
