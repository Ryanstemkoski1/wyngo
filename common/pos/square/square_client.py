from square.client import Client

from common.pos.utils import search
from wyndo.settings import SQUARE_ENVIRONMENT


class SquareRequestClient:
    def __init__(self, access_token, cursor: str = None):
        self.client = Client(access_token=access_token, environment=SQUARE_ENVIRONMENT)
        self.cursor = cursor

    def get_catalog(self):
        catalog = self.client.catalog.list_catalog(
            types="IMAGE,ITEM", cursor=self.cursor
        )

        if catalog.is_error():
            error = search(catalog.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if catalog.is_success():
            return catalog.body
        return None

    def search_catalog_by_date(self, updated_at):
        catalog = self.client.catalog.search_catalog_objects(
            body={
                "begin_time": updated_at,
                "include_deleted_objects": True,
            }
        )
        if catalog.is_error():
            error = search(catalog.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if catalog.is_success():
            return catalog.body
        return None

    def get_stock(self, catalog_id, location_id):
        inventory_counts = self.client.inventory.batch_retrieve_inventory_counts(
            {
                "catalog_object_ids": [catalog_id],
                "location_ids": [location_id],
            }
        )

        if inventory_counts.is_error():
            error = search(inventory_counts.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if inventory_counts.is_success():
            return inventory_counts.body
        return None

    def create_order(self, body):
        order = self.client.orders.create_order(body)

        if order.is_error():
            error = search(order.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if order.is_success():
            return order.body
        return None

    def update_order(self, order_id, order):
        order = self.client.orders.update_order(order_id, order)

        if order.is_error():
            error = search(order.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if order.is_success():
            return order.body
        return None
