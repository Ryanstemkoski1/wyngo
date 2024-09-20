from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import LogoutView
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from common.retailer_utils import RetailerUtils
from .forms import UserForm, LoginForm, UserProfileUpdateForm
from .models import User


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not request.GET.get("url"):
            messages.success(
                request, "You have been successfully logged out", extra_tags="success"
            )
        return response


class SignUpView(TemplateView):
    template_name = "signup.html"

    def post(self, request, *args, **kwargs):
        form = UserForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            terms_conditions = form.cleaned_data["terms_conditions"]

            if not User.validate_email(email):
                messages.error(request, "Invalid email.", extra_tags="error")
                return redirect("sign-up")

            if not User.validate_password(password):
                messages.error(request, "Invalid password.", extra_tags="error")
                return redirect("sign-up")

            if not User.check_passwords_match(password, confirm_password):
                messages.error(request, "Passwords do not match.", extra_tags="error")
                return redirect("sign-up")

            if terms_conditions is False:
                messages.error(
                    request, "Please check terms conditions box", extra_tags="error"
                )
                return redirect("sign-up")

            if not name or not last_name:
                messages.error(
                    request,
                    "Both name and last name must be filled out.",
                    extra_tags="error",
                )
                return redirect("sign-up")

            try:
                User.create_user(
                    email=email,
                    password=password,
                    first_name=name,
                    last_name=last_name,
                    terms_conditions=terms_conditions,
                )
            except ValidationError as e:
                messages.error(request, str(e), extra_tags="error")
                return redirect("sign-up")

            messages.success(
                request, "Account created successfully.", extra_tags="success"
            )

            User.confirmation_email(
                name=name.title(),
                last_name=last_name,
                email=email,
                btn_url=request.build_absolute_uri("/"),
            )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", extra_tags="error")
        return redirect("login")

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class LoginView(TemplateView):
    template_name = "login.html"

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}", extra_tags="error")
            return redirect("login")

        email = form.cleaned_data.get("email").lower()
        password = form.cleaned_data.get("password")
        remember_me = form.cleaned_data.get("remember_me")

        if not remember_me:
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        user = auth.authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password.", extra_tags="error")
            return redirect("login")

        auth.login(request, user)

        # Check retailer
        RetailerUtils.check_and_promote_retailer_admin_account(user.email)

        return redirect("index")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        return render(request, self.template_name)


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "password_reset.html"

    def post(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs["uidb64"])

        if self.user is not None:
            form = SetPasswordForm(self.user, request.POST)

            if form.is_valid():
                self.form_valid(form)
                User.password_reset_done_email(
                    self.user.first_name.title(),
                    self.user.email,
                    request.build_absolute_uri("/login/"),
                )
                return redirect(self.success_url)
            else:
                for field in form:
                    for error in field.errors:
                        messages.error(request, f"{field.label}: {error}", extra_tags="error")
                return redirect(request.path_info)


# @method_decorator(login_required, name="dispatch")
class UserProfileView(TemplateView):
    template_name = "edit_profile.html"

    def post(self, request, *args, **kwargs):
        form = UserProfileUpdateForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data.get("first_name")
            if first_name:
                request.user.first_name = first_name

            last_name = form.cleaned_data.get("last_name")
            if last_name:
                request.user.last_name = last_name

            new_password = form.cleaned_data.get("password")
            if new_password:
                if not request.user.check_password(new_password):
                    request.user.set_password(new_password)
                    update_session_auth_hash(request, request.user)
                else:
                    messages.success(
                        request, "The new password must be different from the current password.", extra_tags="error"
                    )

                    return redirect("profile")

            request.user.save()
            messages.success(
                request, "Your data was updated successfully", extra_tags="success"
            )
        else:
            messages.error(request, "An error occurred while updating the profile.", extra_tags="error")

        return redirect("profile")
