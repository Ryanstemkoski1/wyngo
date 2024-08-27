from django.core.management.base import BaseCommand
from inventories.models import Product, Reservation
from common.pos.clover import CloverReservation

from retailer.models import Retailer


class Command(BaseCommand):
    help = "Cancel Reservation in Clover."

    def handle(self, *args, **options):
        reservation = Reservation.objects.get(origin_id="8TKF12D0MFEW2")

        retailer = (
            Retailer.objects.exclude(access_token__isnull=True)
            .exclude(merchant_id__exact="")
            .filter(merchant_id="HQ7XMXQ558RP1")
            .first()
        )

        if retailer and reservation:
            clover_reservation = CloverReservation(retailer)
            clover_reservation.run(
                {
                    "reservation_params": {
                        "origin_id": reservation.origin_id,
                    }
                },
                "delete",
            )
