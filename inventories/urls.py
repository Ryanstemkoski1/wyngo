from django.urls import path

from . import views

urlpatterns = [
    path("delete_image/<int:image_id>/", views.delete_image, name="delete_image"),
    path(
        "clover/webhook_events",
        views.webhook_clover_events,
        name="webhook_clover_events",
    ),
    path(
        "square/webhook_events",
        views.webhook_square_event,
        name="webhook_square_events",
    ),
]
