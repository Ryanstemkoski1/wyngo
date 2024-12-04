from logging import error as error_log

from django.db import transaction

from common.pos.reservation import Reservation
from common.pos.square import SquareInventory
from common.pos.square.square_client import SquareRequestClient
from common.pos.utils import format_price
from inventories.models import Order as OrderModel, Customer, Variant, OrderItem, OrderPickup
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

        new_order, _created = OrderModel.objects.get_or_create(
            origin_id=order.get("id"), retailer=self._retailer
        )
        new_order.subtotal = format_price(order.get('total_money', {}).get('amount'))
        new_order.tax = format_price(order.get('total_tax_money', {}).get('amount'))
        net_amount = order.get('net_amounts', {}).get('total_money')
        new_order.total = format_price(net_amount.get('amount'))
        new_order.currency = net_amount.get('currency')
        new_order.status = order["state"]
        new_order.order_time = order.get('created_at')
        new_order.retailer = self._retailer
        new_order.origin = self.PLATFORM
        new_order.version = order.get("version", 1)
        new_order.order_code = "#{:06d}".format(new_order.id)
        if order.get("customer_id"):
            customer = Customer.objects.filter(origin_id=order.get("customer_id")).first()
            if customer:
                new_order.customer = customer
        new_order.save()

        fulfillments = order.get("fulfillments", [])
        for fulfillment in fulfillments:
            if fulfillment.get("pickup_details"):
                reservation_pickup, _created = OrderPickup.objects.get_or_create(
                    origin_id=fulfillment.get("uid"),
                    order=new_order
                )
                pickup_details = fulfillment.get("pickup_details")
                reservation_pickup.pickup_time = pickup_details.get("pickup_at")
                reservation_pickup.recipient_name = pickup_details.get("recipient",{}).get("display_name")
                reservation_pickup.save()

        total_quantity = 0
        new_order.order_items.all().delete()
        for line_item in order.get("line_items", []):
            if line_item.get("item_type") != "ITEM":
                continue
            item_id = line_item.get("catalog_object_id")
            quantity = line_item.get("quantity")
            variant = Variant.objects.filter(origin_id=item_id).first()
            if not variant:
                pass
                # square_inventory = SquareInventory(self._retailer)
                # square_inventory.run()
                # variant = Variant.objects.filter(origin_id=item_id).first()
            if variant:
                item, _created = OrderItem.objects.get_or_create(
                    order=new_order, variant=variant, quantity=quantity
                )
                item.unit_price = format_price(line_item.get("base_price_money", {}).get("amount"))
                item.variation_total = format_price(line_item.get("variation_total_price_money", {}).get("amount"))
                item.tax = format_price(line_item.get("total_tax_money", {}).get("amount"))
                item.total_price = format_price(line_item.get("total_money", {}).get("amount"))
                item.save()
            total_quantity += int(quantity)

        new_order.quantity = total_quantity
        new_order.save()


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
