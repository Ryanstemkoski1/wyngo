from square.client import Client

from common.pos.utils import search
from wyndo.settings import SQUARE_ENVIRONMENT


class SquareRequestClient:
    def __init__(self, access_token, cursor: str = None):
        self.client = Client(access_token=access_token, environment=SQUARE_ENVIRONMENT)
        self.cursor = cursor

    def get_catalog(self):
        catalog = self.client.catalog.list_catalog(
            types="IMAGE,ITEM,CATEGORY", cursor=self.cursor
        )

        if catalog.is_error():
            error = search(catalog.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if catalog.is_success():
            return catalog.body
        return None

    def get_catalogs_by_type(self, types: str):
        catalog = self.client.catalog.list_catalog(types=types, cursor=self.cursor)

        if catalog.is_error():
            error = search(catalog.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if catalog.is_success():
            return catalog.body

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

    def retrieve_catalog(self, catalog_id):
        catalog = self.client.catalog.retrieve_catalog_object(catalog_id)
        if catalog.is_error():
            error = search(catalog.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if catalog.is_success():
            return catalog.body

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

    def list_orders(self, locations):
        orders = self.client.orders.search_orders(
            body={"location_ids": locations}
        )
        if orders.is_error():
            raise Exception("[REQUEST CLIENT] " + str(orders.errors))

        if orders.is_success():
            return orders.body
        return None

    def get_order(self, order_id):
        order = self.client.orders.retrieve_order(order_id)
        if order.is_error():
            error = search(order.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if order.is_success():
            return order.body
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

    def list_customers(self):
        customers = self.client.customers.list_customers()
        if customers.is_error():
            error = search(customers.errors, "detail")
            raise Exception("[REQUEST CLIENT] " + error)

        if customers.is_success():
            return customers.body
