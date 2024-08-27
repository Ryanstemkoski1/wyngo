from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError

from .models import User


class UserProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(max_length=128, required=False, widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=128, required=False)
    last_name = forms.CharField(max_length=128, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()

        for key, value in cleaned_data.items():
            if not value:
                cleaned_data[key] = getattr(self.instance, key)

        return cleaned_data


class UserForm(forms.Form):
    name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True, validators=[validators.validate_email])
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput())
    terms_conditions = forms.BooleanField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists.")

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Password and confirm password does not match.")


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    remember_me = forms.BooleanField(required=False)
