import logging

from common.pos.clover.clover_client import CloverRequestClient
from retailer.models import Retailer

logger = logging.getLogger(__name__)


class CloverCustomer:
    @staticmethod
    def handle_event(event: dict, event_type: str) -> None:
        data = event["object"]
        if event_type == "CREATE" or event_type == "UPDATE":
            CloverCustomer.create_or_update_customer(data)
        elif event_type == "DELETE":
            CloverCustomer.delete_customer(data)
        else:
            pass

    @staticmethod
    def delete_customer(data: dict) -> None:
        merchant_id = data["merchant"]["id"]
        retailer = Retailer.objects.get(merchant_id=merchant_id)
        retailer.customers.filter(origin_id=data["id"]).delete()

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

    @staticmethod
    def fetch_all_customers(retailer: Retailer) -> None:
        client = CloverRequestClient(retailer.access_token, retailer.merchant_id)
        customers = client.list_customers()
        for element in customers.get("elements", []):
            _id = element["id"]
            customer = retailer.customers.filter(origin_id=_id).first()

            if not customer:
                customer = retailer.customers.create(origin_id=_id)

            customer.first_name = element["firstName"]
            customer.last_name = element["lastName"]
            customer.origin_id = _id
            customer.retailer = retailer

            email_addresses = element.get("emailAddresses", {}).get("elements", [])
            if len(email_addresses) > 0:
                customer.email = email_addresses[0]['emailAddress']

            addresses = element.get("addresses", {}).get("elements", [])
            if len(addresses) > 0:
                address = addresses[0]
                customer.address1 = address.get('address1')
                customer.address2 = address.get('address2')
                customer.zip_code = address.get('zip')
                customer.city = address.get('city')
                customer.state = address.get('state')
                customer.country = address.get('country')

            phone_numbers = element.get("phoneNumbers", {}).get("elements", [])
            if len(phone_numbers) > 0:
                customer.phone = phone_numbers[0]['phoneNumber']
            customer.save()
