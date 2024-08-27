from django.core.management.base import BaseCommand
from inventories.models import Product, Reservation
from common.pos.clover import CloverReservation

from retailer.models import Retailer


class Command(BaseCommand):
    help = "Update Reservation in Clover."

    def handle(self, *args, **options):
        product = Product.objects.get(origin_id="43W6ZMTDV06J6")
        reservation = Reservation.objects.get(id=11)

        retailer = (
            Retailer.objects.exclude(access_token__isnull=True)
            .exclude(merchant_id__exact="")
            .filter(merchant_id="HQ7XMXQ558RP1")
            .first()
        )

        line_item_params = [
            {"item": {"id": "43W6ZMTDV06J6"}},
            {"item": {"id": "43W6ZMTDV06J6"}},
        ]

        data = {
            "line_item_params": line_item_params,
            "order_params": {
                "order_id": "PJX6YCHXPBMB0",
                "total": (int(12 * 100) * len(line_item_params)),
                "note": "Order updated on Wyndo App",
                "title": "Wyndo Order",
                "state": "OPEN",
                "status": "RESERVED",
            },
            "reservation_params": {
                "quantity": len(line_item_params) + reservation.quantity,
                "status": "RESERVED",
            },
        }

        if retailer:
            clover_reservation = CloverReservation(retailer)
            clover_reservation.run(data, "update")
