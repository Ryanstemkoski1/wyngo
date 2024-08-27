from logging import error as error_log

from django.db import transaction

from common.pos.reservation import Reservation
from common.pos.square.square_client import SquareRequestClient
from common.pos.utils import format_price


class SquareReservation(Reservation):
    PLATFORM = "SQUARE"

    def __init__(self, retailer):
        self._reservation = None
        self._retailer = retailer
        self._request_client = SquareRequestClient(
            retailer.access_token, retailer.merchant_id
        )

    def post(self, payload):
        return self._request_client.create_order(payload.get("order_params"))

    def put(self, payload):
        return self._request_client.update_order(
            payload.get("reservation_params").get("order_id"),
            payload.get("order_params"),
        )

    def delete(self, payload):
        return self._request_client.update_order(
            payload.get("reservation_params").get("order_id"),
            payload.get("order_params"),
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
                "version": reservation["version"],
            }
        )

    def process(self, data):
        mapped_order_data = SquareOrderMapper(data).get_order()
        return self.store(mapped_order_data)

    def run(self, data, action="create"):
        try:
            if action == "update":
                order = self.put(data)

            elif action == "delete":
                order = self.delete(data)
                self.remove(
                    {"origin_id": data.get("reservation_params").get("order_id")}
                )
            else:
                order = self.post(data)

            if action != "delete":
                reservation = {
                    "order": order.get("order"),
                    "reservation": data.get("reservation_params"),
                }

                return self.process(reservation)

        except Exception as e:
            error_log("SQUARE ORDER: %s" % e)


class SquareOrderMapper:
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
            "location_id": order.get("order").get("location_id"),
            "total": format_price(order.get("order").get("total_money").get("amount")),
            "status": order.get("reservation").get("status"),
            "quantity": int(order.get("reservation").get("quantity")),
            "product": order.get("reservation").get("product"),
            "user": order.get("reservation").get("user"),
            "version": int(order.get("order").get("version")),
        }

        self.set_order(order_mappped)
