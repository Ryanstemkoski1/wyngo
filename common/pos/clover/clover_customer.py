import logging

from retailer.models import Retailer

logger = logging.getLogger(__name__)


class CloverCustomer:
    @staticmethod
    def handle_event(event: dict, event_type: str) -> None:
        data = event["object"]
        if event_type == "CREATE" or event_type == "UPDATE":
            CloverCustomer.create_or_update_customer(data)
        else:
            logger.info(f"Event type not supported: {event_type}")

    @staticmethod
    def create_or_update_customer(data: dict) -> None:
        merchant_id = data["merchant"]["id"]
        try:
            retailer = Retailer.objects.get(merchant_id=merchant_id)

        except Retailer.DoesNotExist:
            logger.error(f"Retailer not found for merchant id: {merchant_id}")
            return

        _id = data["id"]
        customer = retailer.customers.filter(origin_id=_id).first()

        if not customer:
            customer = retailer.customers.create(origin_id=_id)

        customer.first_name = data["firstName"]
        customer.last_name = data["lastName"]
        customer.origin_id = _id
        customer.retailer = retailer

        emails = data.get("emailAddresses", [])
        addresses = data.get('addresses', [])

        if len(emails) > 0:
            customer.email = emails[0]['emailAddress']
        if len(addresses) > 0:
            address = addresses[0]
            customer.address1 = address['address1']
            customer.address2 = address['address2']
            customer.zip_code = address['zip']
            customer.city = address['city']
            customer.state = address['state']
            customer.country = address['country']

        customer.save()
