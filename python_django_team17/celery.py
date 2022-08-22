import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "python_django_team17.settings")
app = Celery("python_django_team17")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
