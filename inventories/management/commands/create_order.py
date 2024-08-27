import datetime

from accounts.models import User
from django.core.management.base import BaseCommand
from inventories.models import Product
from common.pos.clover import CloverReservation

from retailer.models import Retailer


class Command(BaseCommand):
    help = "Create Reservation in Clover."

    def handle(self, *args, **options):
        user = User.objects.get(email="decyzoby@mailinator.com")
        product = Product.objects.get(origin_id="43W6ZMTDV06J6")
        retailer = (
            Retailer.objects.exclude(access_token__isnull=True)
            .exclude(merchant_id__exact="")
            .filter(merchant_id="HQ7XMXQ558RP1")
            .first()
        )

        order_data = {
            "orderCart": {
                "lineItems": [
                    {"item": {"id": "43W6ZMTDV06J6"}},
                    {"item": {"id": "43W6ZMTDV06J6"}},
                    {"item": {"id": "43W6ZMTDV06J6"}},
                ],
                "note": "Order created on Wyndo App",
                "title": "Wyndo Order",
                "orderType": {
                    "id": "1KEW2DR2N2RKY",
                },
            }
        }

        reservation_data = {
            "product": product.id,
            "user": user.id,
            "quantity": len(order_data.get("orderCart").get("lineItems")),
            "status": "RESERVED",
        }

        data = {
            "order_params": order_data,
            "reservation_params": reservation_data,
        }

        if retailer:
            clover_reservation = CloverReservation(retailer)
            clover_reservation.run(data, "create")
