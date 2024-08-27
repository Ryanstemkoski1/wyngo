import json

from django.core.cache import cache

from common.pos.square import SquareInventory
from common.pos.square.square_location import SquareLocation
from inventories.tasks import process_square_catalog_event
from retailer.models import Retailer


class SquareWebhook:
    __EVENT_TYPE_KEYS = {
        "location.updated": "LocationUpdated",
        "location.created": "LocationCreated",
        "catalog.version.updated": "CatalogUpdated",
        "inventory.count.updated": "InventoryCountUpdated",
    }

    def process_events(
        self, merchant_id: str, event_id: str, event_type: str, body: dict
    ) -> None:
        event_trace = {
            "event_id": event_id,
            "event_type": event_type,
            "status": "PROCESS",
        }
        cache.set(f"{merchant_id}_{event_id}", json.dumps(event_trace))
        retailer = Retailer.objects.get(merchant_id=merchant_id)
        match self.__EVENT_TYPE_KEYS[event_type]:
            case "LocationUpdated":
                SquareLocation.create_or_update_location(
                    retailer=retailer, location_id=merchant_id
                )
            case "LocationCreated":
                SquareLocation.create_or_update_location(
                    retailer=retailer, location_id=merchant_id
                )
            case "CatalogUpdated":
                process_square_catalog_event.delay(body=body, retailer_id=retailer.pk)
            case "InventoryCountUpdated":
                square_inventory = SquareInventory(retailer)
                square_inventory.webhook_update_variant_stock(body)
            case _:
                pass

        event_trace["status"] = "SUCCESS"
        cache.set(f"{merchant_id}_{event_id}", json.dumps(event_trace))
