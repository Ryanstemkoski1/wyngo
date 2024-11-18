import logging

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(email__iexact=username)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_("email address"), blank=False, unique=True)
    terms_conditions = models.BooleanField(
        "By Creating an account, I have read an agree to Wyndo", default=False
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.email.lower()

    @staticmethod
    def validate_email(email):
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    @staticmethod
    def validate_password(password):
        try:
            validate_password(password)
            return True
        except ValidationError:
            return False

    @staticmethod
    def check_passwords_match(password, confirm_password):
        return password == confirm_password

    @staticmethod
    def create_user(email, password, first_name, last_name, terms_conditions):
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already in use.")

        if not User.validate_email(email):
            raise ValidationError("Invalid email.")

        if not User.validate_password(password):
            raise ValidationError("Invalid password.")

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            terms_conditions=terms_conditions,
        )
        return user

    @staticmethod
    def send_email(message, email, subject):
        mail = EmailMessage(
            subject=subject,
            body=message,
            to=[email],
        )
        mail.content_subtype = "html"
        mail.send()

    @staticmethod
    def confirmation_email(name, last_name, email, btn_url):
        try:
            # TODO: Add logic to get products from database
            message = render_to_string(
                "email_template_signup.html",
                {
                    "name": name,
                    "LAST_NAME": last_name,
                    "EMAIL": email,
                    "btn_url": btn_url,
                    "products": [
                        {
                            "price": 2.50,
                            "description": "Great value PB sandwich cookie",
                            "image": "https://i5.walmartimages.com/asr/871cf51b-73ec-4499-9994-0ac5d4b37dc4.d1ea7206f303a0c06027ca2a36414b59.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                        {
                            "price": 1.25,
                            "description": "Special order basic cupcakes",
                            "image": "https://i5.walmartimages.com/asr/2af0f1fd-5728-4e1b-a16a-68549e466b2f.65a243bd75c499fb1545fa0d8d2ec16e.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                        {
                            "price": 3.99,
                            "description": "OREO chocolate sandwich cookies",
                            "image": "https://i5.walmartimages.com/asr/3c46a2bc-1837-4738-9777-04d7bf33bb30.e65134ebcba515950d7b89af7a9ccba6.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                        {
                            "price": 1.66,
                            "description": "Coca-Cola Soda Pop, 12 fl oz",
                            "image": "https://i5.walmartimages.com/asr/db183a97-8513-4c58-8d6b-ef706bbadc57.83eb40f19568083f8c49c1eb33802327.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                    ],
                },
            )

            User.send_email(message, email, "Account created successfully")
        except Exception as e:
            logging.error(str(e))

    @staticmethod
    def password_reset_done_email(name, email, btn_url):
        try:
            # TODO: Add logic to get products from database
            message = render_to_string(
                "email_template_password_reset_done.html",
                {
                    "name": name,
                    "btn_url": btn_url,
                    "products": [
                        {
                            "price": 2.50,
                            "description": "Great value PB sandwich cookie",
                            "image": "https://i5.walmartimages.com/asr/871cf51b-73ec-4499-9994-0ac5d4b37dc4.d1ea7206f303a0c06027ca2a36414b59.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                        {
                            "price": 1.25,
                            "description": "Special order basic cupcakes",
                            "image": "https://i5.walmartimages.com/asr/2af0f1fd-5728-4e1b-a16a-68549e466b2f.65a243bd75c499fb1545fa0d8d2ec16e.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                        {
                            "price": 3.99,
                            "description": "OREO chocolate sandwich cookies",
                            "image": "https://i5.walmartimages.com/asr/3c46a2bc-1837-4738-9777-04d7bf33bb30.e65134ebcba515950d7b89af7a9ccba6.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                        {
                            "price": 1.66,
                            "description": "Coca-Cola Soda Pop, 12 fl oz",
                            "image": "https://i5.walmartimages.com/asr/db183a97-8513-4c58-8d6b-ef706bbadc57.83eb40f19568083f8c49c1eb33802327.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                        },
                    ],
                },
            )

            User.send_email(message, email, "Password reset successfully")
        except Exception as e:
            logging.error(str(e))

    @staticmethod
    def password_reset_email(name, email, opts):
        try:
            # TODO: Add logic to get products from database
            message = render_to_string(
                "email_template_forgot_password.html",
                {
                    "opts": opts,
                },
            )

            User.send_email(message, email, "Reset your password")
        except Exception as e:
            logging.error(str(e))
