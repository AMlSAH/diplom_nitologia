import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_service.settings')

app = Celery('retail_service')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
