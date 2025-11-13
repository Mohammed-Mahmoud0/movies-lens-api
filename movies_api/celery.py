"""
Celery Configuration for movies_api project
"""
import os
from celery import Celery

# Set default Django settings module for 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies_api.settings')

# Create Celery app
app = Celery('movies_api')

# Load config from Django settings with 'CELERY_' namespace
# This means all celery-related settings should start with 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all installed apps
# Looks for tasks.py in each app directory
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """
    Debug task to test Celery is working
    """
    print(f'Request: {self.request!r}')
