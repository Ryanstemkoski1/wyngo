from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from .views import (
    SignUpView,
    LoginView,
    CustomLogoutView,
    CustomPasswordResetConfirmView,
    UserProfileView,
)


urlpatterns = [
    path("signup/", SignUpView.as_view(), name="sign-up"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path(
        "forgot_password/",
        auth_views.PasswordResetView.as_view(
            template_name="forgot_password.html",
            html_email_template_name="email_template_forgot_password.html",
            subject_template_name="password_reset_subject.txt",
        ),
        name="forgot_password",
    ),
    path(
        "forgot_password/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="forgot_password_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password_reset/confirm/<str:uidb64>/<str:token>",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
