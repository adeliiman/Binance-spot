import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "salon_manager.settings")

app = Celery("salon_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()