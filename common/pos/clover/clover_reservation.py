from logging import error as error_log

from django.db import transaction

from common.pos.clover.clover_client import CloverRequestClient
from common.pos.reservation import Reservation
from common.pos.utils import format_price


class CloverReservation(Reservation):
    PLATFORM = "CLOVER"

    def __init__(self, retailer):
        super().__init__(retailer)
        self._request_client = CloverRequestClient(
            retailer.access_token, retailer.merchant_id
        )

    def post(self, payload):
        print("post")
        return self._request_client.create_order(payload.get("order_params"))

    def put(self, payload):
        self._request_client.remove_line_items(
            payload.get("order_params").get("order_id"),
        )

        for item in payload.get("line_item_params"):
            self._request_client.add_line_item(
                payload.get("order_params").get("order_id"),
                item,
            )

        return self._request_client.update_order(
            payload.get("order_params").get("order_id"), payload.get("order_params")
        )

    def delete(self, payload):
        return self._request_client.delete_order(
            payload.get("reservation_params").get("origin_id")
        )

    @transaction.atomic
    def store(self, reservation):
        return self.update_or_create_reservation(
            {
                "origin": self.PLATFORM,
                "origin_id": reservation["origin_id"],
                "status": reservation["status"],
                "quantity": reservation["quantity"],
                "product": reservation["product"],
                "user": reservation["user"],
                "total": reservation["total"],
            }
        )

    def process(self, data):
        mapped_order_data = CloverOrderMapper(data).get_order()
        return self.store(mapped_order_data)

    def run(self, data, action="create"):
        try:
            if action == "update":
                order = self.put(data)
            elif action == "delete":
                order = self.delete(data)
                self.remove(
                    {"origin_id": data.get("reservation_params").get("origin_id")}
                )
            else:
                order = self.post(data)

            if action != "delete":
                reservation = {
                    "order": order,
                    "reservation": data.get("reservation_params"),
                }

                return self.process(reservation)

        except Exception as e:
            error_log("CLOVER ORDER: %s" % e)


class CloverOrderMapper:
    def __init__(self, order):
        self._order = order
        self.map_order(order)

    def get_order(self):
        return self._order

    def set_order(self, order):
        self._order = order

    def map_order(self, order):
        order_mappped = {
            "origin_id": order.get("order").get("id"),
            "total": format_price(order.get("order").get("total")),
            "status": order.get("reservation").get("status"),
            "quantity": len(order.get("order").get("lineItems").get("elements")),
            "product": order.get("reservation").get("product"),
            "user": order.get("reservation").get("user"),
        }

        self.set_order(order_mappped)
