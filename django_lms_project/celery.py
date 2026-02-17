import os

from celery import Celery

# Указываем правильный модуль настроек
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_lms_project.settings")

app = Celery("django_lms_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
