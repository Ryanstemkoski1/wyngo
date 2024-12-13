import csv
import os
from io import StringIO

import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.http import HttpResponse

from common.models import BaseTimeModel
from retailer.models import Retailer


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
    origin_id = models.CharField(max_length=50, null=True, default=None, unique=True)
    retailer = models.ForeignKey(
        Retailer, on_delete=models.CASCADE, related_name="categories",
    )
    variants = models.ManyToManyField("Variant", blank=True, related_name="categories")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    @property
    def items(self):
        return self.variants.all().count()


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

    # category = models.ForeignKey(
    #     Category, on_delete=models.SET_NULL, null=True, blank=True, default=None
    # )

    origin_id = models.CharField(max_length=50, null=True, default=None)

    total_stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField("Active Status", default=True)

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

    @property
    def category(self):
        all_categories = self.variants.first().categories.all()
        return ", ".join([category.name for category in all_categories])

    def is_single_product(self):
        variants = self.variants.all()
        if len(variants) > 1:
            return False
        return len(variants) == 0 or variants[0].origin_id == self.origin_id


class Variant(BaseTimeModel):
    name = models.CharField(max_length=255)

    sku = models.CharField(max_length=255, null=True, blank=True)

    upc = models.CharField(max_length=255, null=True, blank=True)

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
        return f"{self.product.name} - {self.name}"

    @property
    def full_name(self):
        return f"{self.product.name} - {self.name}"


class VariantImage(BaseTimeModel):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

    image = models.ImageField(upload_to="inventories", null=True, blank=True, max_length=511)

    image_id = models.CharField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.image}"

    def get_image_from_url(self, url):
        r = requests.get(url)
        if r.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            img_temp.flush()

            try:
                file_name = f"{self.image_id}-{os.path.basename(url)}"
                self.image.save(file_name, File(img_temp), save=True)
            except:
                print("Failed downloading image from " + url)
                return False
            else:
                return True


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

    def __str__(self):
        return f"Reservation {self.reservation_code}"

    class Meta:
        ordering = ["-created_at"]


class Customer(BaseTimeModel):
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    address1 = models.CharField(max_length=255, null=True, blank=True)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    address3 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    retailer = models.ForeignKey(
        Retailer, on_delete=models.SET_NULL, null=True, default=None, related_name="customers"
    )
    origin_id = models.CharField(max_length=50, null=True, default=None, unique=True)

    def full_address(self):
        address = ""
        if self.address1:
            address += self.address1
        if self.address2:
            address += ", " + self.address2
        if self.address3:
            address += ", " + self.address3
        if self.city:
            address += ", " + self.city
        if self.state:
            address += ", " + self.state
        if self.country:
            address += ", " + self.country
        return address

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(BaseTimeModel):
    CLOVER = "CLOVER"
    SQUARE = "SQUARE"

    ORIGIN_CHOICES = ((CLOVER, CLOVER), (SQUARE, SQUARE))

    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    origin_id = models.CharField(max_length=50, null=True, default=None, unique=True)
    origin = models.CharField(
        max_length=10, choices=ORIGIN_CHOICES, null=True, default=None
    )
    status = models.CharField(max_length=20, default="SUCCESS")
    quantity = models.IntegerField(default=0)
    time_limit = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name="reservations"
    )
    order_code = models.CharField(max_length=100, null=True, blank=True, unique=True)
    retailer = models.ForeignKey(
        Retailer, on_delete=models.SET_NULL, null=True, blank=True, default=None, related_name="reservations"
    )

    version = models.PositiveIntegerField(default=1)
    order_time = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def generate_report_csv(orders, created_at_range_gte, created_at_range_lte):
        output = StringIO()
        writer = csv.writer(output)

        headers = [
            "Order ID",
            "Origin",
            "Retailer",
            "Total",
            "Status",
            "Quantity",
            "Items",
            "Variant",
            "Price",
            "Price Per Unit",
            "Customer Name",
            "Customer Email",
            "Customer Phone",
            "Customer Address",
            "Reserved Date",
            "Updated Date",
        ]
        writer.writerow(headers)

        for order in orders:
            customer = order.customer
            customer_name = order.customer.first_name + " " + order.customer.last_name \
                if order.customer else ""
            line_items = order.order_items.all()
            for item in line_items:
                if item.item_type == item.TYPE_ITEM:
                    variant = item.variant
                    item_name = variant.product.name
                    variant_name = variant.name
                else:
                    item_name = item.name
                    variant_name = ""
                row = [
                    order.order_code,
                    order.origin,
                    order.retailer.name if order.retailer else "",
                    f"$ {order.total}",
                    order.status,
                    item.quantity,
                    item_name,
                    variant_name,
                    item.variation_total,
                    item.unit_price,
                    customer_name,
                    customer.email if customer else "",
                    customer.phone if customer else "",
                    customer.full_address() if customer else "",
                    order.order_time.strftime("%d-%m-%y %H:%M:%S")
                            if order.order_time else order.created_at.strftime("%d-%m-%y %H:%M:%S"),
                    order.updated_at.strftime("%d-%m-%y %H:%M:%S"),
                ]
                writer.writerow(row)

        response = HttpResponse(content=output.getvalue(), content_type="text/csv")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="order_reports.csv"'

        return response

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-order_time"]

    def __str__(self):
        return f"{self.order_code}"


class OrderItem(BaseTimeModel):
    TYPE_ITEM = 1
    TYPE_CUSTOM_AMOUNT = 2
    ITEM_TYPES = ((TYPE_ITEM, "Item"), (TYPE_CUSTOM_AMOUNT, "Custom Amount"))

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="order_items", null=True)
    quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    variation_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    item_type = models.PositiveSmallIntegerField(max_length=20, choices=ITEM_TYPES, default=TYPE_ITEM)

    class Meta:
        verbose_name = "Reservation Item"
        verbose_name_plural = "Reservation Items"

    @property
    def order_time(self):
        return self.order.order_time

    @property
    def name(self):
        if self.item_type == self.TYPE_CUSTOM_AMOUNT:
            return "Custom Amount"
        if self.item_type == self.TYPE_ITEM:
            return str(self.variant.full_name) if self.variant else "Unknown"
        return None

    def __str__(self):
        return f"{self.order} - {self.variant}"


class OrderPickup(BaseTimeModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="reservation_pickups")
    recipient_name = models.CharField(max_length=255, null=True, blank=True)
    pickup_time = models.DateTimeField(null=True, blank=True)
    origin_id = models.CharField(max_length=50, null=True, default=None, unique=True)

    class Meta:
        verbose_name = "Pickup"
        verbose_name_plural = "Pickup"

    @property
    def location(self):
        return self.order.retailer.location_set.first()

    def __str__(self):
        return f"Pickup - {self.order} - {self.pickup_time}"
