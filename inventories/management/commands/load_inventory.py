import logging

from django.conf import settings
from django.core.mail import send_mail

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

        send_mail(
            "Test",
            "hello donnie.patrick077@gmail.com",
            "elliott@wyndoshop.com",
            ["donnie.patrick077@gmail.com", "donnie.patrick077@example.com", "donnie.patrick078@example.com",
             "donnie.patrick080@example.com"],
            fail_silently=False,
        )
        print('sent')

        # retailers = Retailer.objects.exclude(access_token__isnull=True).exclude(
        #     merchant_id__exact=""
        # )
        #
        # if retailers:
        #     for retailer in retailers:
        #         origin = retailer.origin
        #
        #         if origin == "CLOVER":
        #             clover_inventory = CloverInventory(retailer)
        #             clover_inventory.run()
        #         elif origin == "SQUARE":
        #             square_inventory = SquareInventory(retailer)
        #             square_inventory.run()
        #         else:
        #             continue
