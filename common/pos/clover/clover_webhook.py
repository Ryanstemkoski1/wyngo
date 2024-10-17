import logging

from django.core.mail import EmailMessage

from accounts.models import User
from common.pos.clover import CloverInventory
from common.pos.clover.clover_customer import CloverCustomer
from common.pos.clover.clover_location import CloverLocation
from common.pos.clover.clover_reservation import CloverReservation
from inventories.tasks import run_go_upc_integration
from retailer.models import Retailer

logger = logging.getLogger(__name__)


class CloverWebhook:
    __EVENT_TYPE_KEYS = {
        "A": "Apps",
        "C": "Customers",
        "CA": "Cash Adjustments",
        "E": "Employees",
        "I": "Inventory",
        "IC": "Inventory Category",
        "IG": "Inventory Modifier Group",
        "IM": "Inventory Modifier",
        "O": "Orders",
        "M": "Merchants",
        "P": "Payments",
    }

    __TYPE_CREATE = "CREATE"
    __TYPE_UPDATE = "UPDATE"
    __TYPE_DELETE = "DELETE"

    def process_events(self, body: dict) -> None:
        app_id = body["appId"]
        for merchant_id, objects in body["merchants"].items():
            retailer = (
                Retailer.objects.filter(origin=Retailer.CLOVER)
                .filter(app_id=app_id)
                .filter(merchant_id=merchant_id)
                .filter(status=Retailer.STATUS_APPROVED)
                .first()
            )
            if not retailer:
                return

            clover_inventory = CloverInventory(retailer)

            for event in objects:
                event_type, object_id = event["objectId"].split(":")
                match self.__EVENT_TYPE_KEYS[event_type]:
                    case "Inventory":
                        # Inventory Type Event
                        if event["type"] in [self.__TYPE_CREATE, self.__TYPE_UPDATE]:
                            # Inventory Creation/Update Event
                            clover_inventory.run(item_id=object_id)
                            run_go_upc_integration.delay(retailer_id=retailer.pk)

                        elif event["type"] == self.__TYPE_DELETE:
                            # Inventory Creation Event
                            clover_inventory.delete(item_id=object_id)
                    case "Inventory Category":
                        if event["type"] in [self.__TYPE_CREATE, self.__TYPE_UPDATE]:
                            clover_inventory.create_or_update_category(event.get("object", {}))
                        elif event["type"] == self.__TYPE_DELETE:
                            clover_inventory.delete_category(category_id=object_id)
                    case "Merchants":
                        if event["type"] == self.__TYPE_UPDATE:
                            # Merchant Update Event
                            # Update location
                            CloverLocation.fetch_locations(merchant_id=object_id)
                    case "Customers":
                        CloverCustomer.handle_event(event, event['type'])
                    case "Orders":
                        clover_reservation = CloverReservation(retailer)
                        if event["type"] == self.__TYPE_UPDATE or event["type"] == self.__TYPE_CREATE:
                            clover_reservation.sync_from_clover(object_id)
                    case _:
                        pass

    @staticmethod
    def send_verification_email(verification_code) -> bool:
        address = (
            User.objects.filter(is_superuser=True).order_by("date_joined").first()
        ).email
        if address:
            subject = "Clover Verification Code"
            message = f"Your Clover verification code is: {verification_code}"
            recipient_list = [
                address,
            ]
            email = EmailMessage(subject=subject, body=message, to=recipient_list)
            email.send()

            return True

        return False
