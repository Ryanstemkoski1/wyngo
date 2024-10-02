import logging

from common.pos.square.square_inventory import SquareInventory

from retailer.models import Retailer
from common.pos.clover import CloverInventory
from django.core.management.base import BaseCommand


# TODO: Delete command at the end of testing
class Command(BaseCommand):
    help = "Get Inventories From Clover and Square."

    def add_arguments(self, parser):
        parser.add_argument(
            '--offset',
            type=int,
            default=0,
            help='Offset pagination'
        )

        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Límit pagination'
        )

    def handle(self, *args, **options):
        logging.info("Starting inventory loading process")

        retailers = Retailer.objects.exclude(access_token__isnull=True).exclude(
            merchant_id__exact=""
        )

        if retailers:
            for retailer in retailers:
                origin = retailer.origin

                if origin == "CLOVER":
                    clover_inventory = CloverInventory(retailer)
                    clover_inventory.run()
                elif origin == "SQUARE":
                    square_inventory = SquareInventory(retailer)
                    square_inventory.run()
                else:
                    continue
