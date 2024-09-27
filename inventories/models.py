import csv
from io import StringIO

from django.db import models
from django.http import HttpResponse

from common.models import BaseTimeModel


class Inventory(BaseTimeModel):
    name = models.CharField(max_length=50, null=True, default=None)
    location = models.ForeignKey(
        "retailer.Location", null=True, on_delete=models.CASCADE, unique=True
    )

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.name}"


class Category(BaseTimeModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(BaseTimeModel):
    CLOVER = "CLOVER"
    SQUARE = "SQUARE"

    ORIGIN_CHOICES = ((CLOVER, CLOVER), (SQUARE, SQUARE))

    name = models.CharField(max_length=255, null=True, default=None)

    max_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    min_price = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True
    )

    origin = models.CharField(
        max_length=10, choices=ORIGIN_CHOICES, null=True, default=None
    )

    inventory = models.ForeignKey(
        Inventory, on_delete=models.CASCADE, null=True, default=None
    )

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )

    origin_id = models.CharField(max_length=50, null=True, default=None)

    total_stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    is_modified_by_admin = models.BooleanField(
        "Modified by Wyndo",
        help_text="When activated the name won't be updated by the app",
        default=False,
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

        unique_together = (
            "origin_id",
            "inventory",
        )

    def __str__(self):
        return f"{self.name}"

    def is_single_product(self):
        variants = self.variants.all()
        if len(variants) > 1:
            return False
        return len(variants) == 0 or variants[0].origin_id == self.origin_id



class Variant(BaseTimeModel):
    name = models.CharField(max_length=255)

    sku = models.CharField(max_length=20, null=True, blank=True)

    upc = models.CharField(max_length=20, null=True, blank=True)

    description = models.TextField(null=True, blank=True, default="")

    stock = models.IntegerField(null=True, blank=True, default=0)

    price = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name="variants",
    )

    origin_id = models.CharField(max_length=50, null=True, default=None)

    origin_parent_id = models.CharField(max_length=50, null=True, default=None)

    currency = models.CharField(max_length=3, default="USD")

    is_modified_by_admin = models.BooleanField(
        "Modified by Wyndo",
        help_text="When activated the description and name won't be updated by the app",
        default=False,
    )

    def get_images(self):
        return self.variantimage_set.all()

    class Meta:
        verbose_name = "Product Detail"
        verbose_name_plural = "Variations"

    def __str__(self):
        return f"{self.name}"


class VariantImage(BaseTimeModel):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="inventories", null=True, blank=True)

    image_id = models.CharField(max_length=100, null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.image}"


class Reservation(BaseTimeModel):
    CLOVER = "CLOVER"
    SQUARE = "SQUARE"

    ORIGIN_CHOICES = ((CLOVER, CLOVER), (SQUARE, SQUARE))

    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    origin_id = models.CharField(max_length=50, null=True, default=None)
    origin = models.CharField(
        max_length=10, choices=ORIGIN_CHOICES, null=True, default=None
    )
    status = models.CharField(max_length=20, default="SUCCESS")
    quantity = models.IntegerField(default=0)
    time_limit = models.DateTimeField(null=True, blank=True)
    variant = models.ForeignKey(
        Variant, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    reservation_code = models.CharField(max_length=100, null=True, blank=True)

    version = models.PositiveIntegerField(default=1)

    @staticmethod
    def generate_report_csv(reservations, created_at_range_gte, created_at_range_lte):
        output = StringIO()
        writer = csv.writer(output)

        headers = [
            "Origin ID",
            "Origin",
            "Total",
            "Status",
            "Quantity",
            "Time Limit",
            "Variant",
            "Full Name",
            "User",
            "Reservation Code",
            "Created Date",
            "Updated Date",
        ]
        writer.writerow(headers)

        for reservation in reservations:
            row = [
                reservation.origin_id,
                reservation.origin,
                f"$ {reservation.total}",
                reservation.status,
                reservation.quantity,
                reservation.time_limit.strftime("%d-%m-%y %H:%M:%S"),
                str(reservation.variant),
                f"{reservation.user.first_name} {reservation.user.last_name}",
                f"{reservation.user.email}",
                reservation.reservation_code,
                reservation.created_at.strftime("%d-%m-%y %H:%M:%S"),
                reservation.updated_at.strftime("%d-%m-%y %H:%M:%S"),
            ]
            writer.writerow(row)

        response = HttpResponse(content=output.getvalue(), content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="reservation_reports.csv"'

        return response

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"

    def __str__(self):
        return f"{self.origin_id}"
