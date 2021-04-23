import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kittygram.settings')

app = Celery('kittygram')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()