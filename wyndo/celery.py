import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wyndo.settings")

app = Celery("wyndo")

app.config_from_object("django.conf:settings", namespace="CELERY_")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "load-clover-category": {
        "task": "inventories.tasks.fetch_clover_categories",
        "schedule": crontab(minute="0", hour="8,13,15"),
    },
    "load-clover-inventory": {
        "task": "inventories.tasks.load_clover_inventory",
        "schedule": crontab(minute="5", hour="8,13,15"),
    },
    "load-clover-customer": {
        "task": "inventories.tasks.fetch_clover_customer",
        "schedule": crontab(minute="10", hour="8,13,15"),
    },
    "load-clover-order": {
        "task": "inventories.tasks.fetch_clover_orders",
        "schedule": crontab(minute="15", hour="8,13,15"),
    },
    "load-square-category": {
        "task": "inventories.tasks.fetch_square_categories",
        "schedule": crontab(minute="20", hour="8,13,15"),
    },
    "load-square-inventory": {
        "task": "inventories.tasks.load_square_inventory",
        "schedule": crontab(minute="30", hour="8,13,15"),
    },
    "load-square-customer": {
        "task": "inventories.tasks.fetch_square_customer",
        "schedule": crontab(minute="35", hour="8,13,15"),
    },
    "load-square-order": {
        "task": "inventories.tasks.fetch_square_orders",
        "schedule": crontab(minute="40", hour="8,13,15"),
    },
    "refresh_token_task": {
        "task": "retailer.task.refresh_token_task",
        "schedule": crontab(minute="0", hour="0"),
    },

    "delete_abaandoned_reservations": {
        "task": "inventories.tasks.delete_abandoned_reservations",
        "schedule": crontab(minute="*/1"),
    },
}
