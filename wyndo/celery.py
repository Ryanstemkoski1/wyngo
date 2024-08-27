import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wyndo.settings")

app = Celery("wyndo")

app.config_from_object("django.conf:settings", namespace="CELERY_")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "load-clover-inventory": {
        "task": "inventories.tasks.load_clover_inventory",
        "schedule": crontab(minute="0", hour="8,13,15"),
    },
    "load-square-inventory": {
        "task": "inventories.tasks.load_square_inventory",
        "schedule": crontab(minute="10,10,10", hour="8,13,15"),
    },
    "refresh_token_task": {
        "task": "retailer.task.refresh_token_task",
        "schedule": crontab(minute="0", hour="0"),
    },
}
