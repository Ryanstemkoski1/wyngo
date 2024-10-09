from logging import error as error_log

from django.db import transaction

from common.pos.reservation import Reservation
from common.pos.square.square_client import SquareRequestClient
from common.pos.utils import format_price
from inventories.models import Reservation as ReservationModel, Customer, Variant, ReservationItem
from retailer.models import Location


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

    def fetch_all_orders(self):
        locations = Location.objects.filter(retailer=self._retailer).values_list(
            'pos_id', flat=True
        )
        rs = self._request_client.list_orders(list(locations))
        all_orders = rs.get("orders", [])
        for order in all_orders:
            order_id = order.get("order_id")
            try:
                self.sync_from_square(order_id, order)
            except Exception as e:
                error_log("SQUARE ORDER: %s" % e)

    def sync_from_square(self, order_id, order=None):
        order = self._request_client.get_order(order_id).get("order") if not order else order
        if not order:
            return

        reservation, _created = ReservationModel.objects.get_or_create(
            origin_id=order.get("id"), retailer=self._retailer
        )
        reservation.total = order["total_money"]["amount"]
        reservation.status = order["state"]
        reservation.retailer = self._retailer
        reservation.origin = self.PLATFORM
        reservation.reservation_code = "#{:06d}".format(reservation.id)
        if order.get("customer_id"):
            customer = Customer.objects.filter(origin_id=order.get("customer_id")).first()
            if customer:
                reservation.customer = customer

        reservation.save()

        for line_item in order.get("line_items", []):
            item_id = line_item.get("catalog_object_id")
            quantity = line_item.get("quantity")
            variant = Variant.objects.filter(origin_id=item_id).first()
            if variant:
                ReservationItem.objects.get_or_create(
                    reservation=reservation, variant=variant, quantity=quantity
                )
            else:
                # todo fetch variant from square
                pass


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
