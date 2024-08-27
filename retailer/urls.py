from django.urls import path

from . import views

urlpatterns = [
    path("square/oauth_callback", views.square_callback, name="square_callback"),
    path("signup/<str:origin>", views.RetailerSignupView.as_view(), name="sign_up"),
    path("connect_pos", views.connect_pos, name="connect_pos"),
]
