import logging
from datetime import datetime

from django.core.mail import EmailMessage
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt

from common.models import BaseTimeModel


# from shopper.models import Category


class Retailer(BaseTimeModel):
    CLOVER = "CLOVER"
    SQUARE = "SQUARE"

    ORIGIN_CHOICES = ((CLOVER, CLOVER), (SQUARE, SQUARE))

    STATUS_REQUESTING = "requesting"
    STATUS_APPROVED = "approved"
    STATUS_DENIED = "denied"
    STATUS_CHOICES = (
        (STATUS_REQUESTING, STATUS_REQUESTING),
        (STATUS_APPROVED, STATUS_APPROVED),
        (STATUS_DENIED, STATUS_DENIED)
    )

    name = models.CharField(max_length=30)

    email = models.EmailField(_("email address"), blank=True, db_index=True)

    description = models.TextField(max_length=280)

    image = models.ImageField(upload_to="retail", null=True, blank=True)

    origin = models.CharField(max_length=7, choices=ORIGIN_CHOICES, db_index=True)

    category = models.ManyToManyField("retailer.Category")

    app_id = models.CharField(
        max_length=50,
        help_text="Please carefully review the entered value to ensure it is correct.",
        db_index=True
    )

    app_secret = models.CharField(
        max_length=100,
        help_text="Please carefully review the entered value to ensure it is correct.",
    )

    merchant_id = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)

    access_token = encrypt(models.CharField(max_length=100, null=True, blank=True, db_index=True))

    refresh_token = encrypt(models.CharField(max_length=100, null=True, blank=True, db_index=True))

    token_type = models.CharField(max_length=50, null=True, blank=True, db_index=True)

    token_created_at = models.DateTimeField(
        verbose_name="Token Creation Date",
        null=True,
        blank=True,
    )

    expires_at = models.DateTimeField(
        verbose_name="Expiration Date", null=True, blank=True
    )

    shopping_center = models.ForeignKey(
        "retailer.ShoppingCenter", null=True, blank=True, on_delete=models.SET_NULL
    )

    square_csrf = models.CharField(max_length=50, null=True, blank=True)

    is_sync = models.BooleanField(default=False)

    status = models.CharField(max_length=12, default=STATUS_REQUESTING, choices=STATUS_CHOICES, db_index=True)
    
    note = models.TextField(default=None, blank=True, null=True)

    # TODO: add a field indicating that it is successfully connected (is_connected=True|False)

    def __str__(self):
        return f"{self.name}"

    def is_access_token_expired(self) -> bool:
        if self.access_token is None:
            return False

        now = timezone.make_aware(datetime.now(), timezone.get_current_timezone())

        expired = self.expires_at < now

        return expired

    def disconnect_retailer(self) -> bool:
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.token_created_at = None
        self.token_type = None
        self.square_csrf = None

        return self.save()

    def update_sync(self, is_sync: bool):
        self.is_sync = is_sync
        self.save()

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
    def register_retailer_email(request_number, email):
        try:
            message = render_to_string(
                "email_template_register_retailer.html",
                {
                    "request_number": request_number,
                },
            )

            Retailer.send_email(message, email, "Request received successfully")
        except Exception as e:
            logging.error(str(e))

    @staticmethod
    def register_admin_email(email, url):
        try:
            message = render_to_string(
                "email_template_register_admin.html",
                {
                    "url": url,
                },
            )

            Retailer.send_email(message, email, "You have a new request to review")
        except Exception as e:
            logging.error(str(e))

    @staticmethod
    def approved_retailer_email(origin, email, url, business_name):
        try:
            message = render_to_string(
                "email_template_approved_retailer.html",
                {
                    "business_name": business_name,
                    "origin": origin,
                    "url": url,
                },
            )

            Retailer.send_email(message, email, "Application approved")
        except Exception as e:
            logging.error(str(e))


class Location(BaseTimeModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    address3 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=100, null=True, blank=True)
    pos_id = models.CharField(max_length=100, null=True, blank=True)
    retailer = models.ForeignKey(
        "retailer.Retailer", null=True, blank=True, on_delete=models.CASCADE
    )

    def update_location(
        self,
        address1: str,
        city: str,
        country: str,
        state: str,
        zip_code: str,
        address2: str = None,
        address3: str = None,
        pos_id: str = None,
        name: str = None,
        **kwargs,
    ):
        # REVIEW: Added `**kwargs` since Clover's response returns 'phoneNumber' even though it doesn't appear in the
        #  documentation
        self.address1 = address1
        self.address2 = address2
        self.address3 = address3
        self.city = city
        self.country = country
        self.state = state
        self.zip_code = zip_code
        self.pos_id = pos_id if self.pos_id is None else self.pos_id
        self.name = name

    def __str__(self):
        values = [self.address1, self.city, self.state, self.country]
        return ", ".join([i for i in values if i])


class Category(BaseTimeModel):
    CANDLE = "candle"
    BAKERIES = "bakery_dining"
    CHECKROOM = "checkroom"
    STOREFRONT = "storefront"
    CONTENT_CUT = "content_cut"
    RESTAURANT = "restaurant"

    ICON_CHOICES = (
        (CANDLE, CANDLE),
        (BAKERIES, BAKERIES),
        (CHECKROOM, CHECKROOM),
        (STOREFRONT, STOREFRONT),
        (CONTENT_CUT, CONTENT_CUT),
        (RESTAURANT, RESTAURANT),
    )

    name = models.CharField(max_length=50)

    icon = models.CharField(choices=ICON_CHOICES, max_length=15, default="")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class ShoppingCenter(BaseTimeModel):
    name = models.CharField(max_length=30)

    description = models.TextField()

    address = models.TextField()

    image = models.ImageField(upload_to="shoppercenter")

    category = models.ManyToManyField(
        Category,
    )

    def __str__(self):
        return f"{self.name}"
