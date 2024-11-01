import logging

from common.pos.square.square_client import SquareRequestClient
from inventories.models import Customer

logger = logging.getLogger(__name__)


class SquareCustomer:
    @staticmethod
    def update_or_create_customer(retailer, payload):
        raw_customer = payload["customer"]
        SquareCustomer.store(raw_customer, retailer)

    @staticmethod
    def store(raw_customer, retailer):
        _id = raw_customer["id"]
        customer = Customer.objects.filter(origin_id=_id).first()
        if not customer:
            customer = retailer.customers.create(origin_id=_id)

        customer.retailer = retailer
        customer.first_name = raw_customer.get("given_name")
        customer.last_name = raw_customer.get("family_name")
        customer.origin_id = _id
        customer.email = raw_customer.get("email_address")
        customer.phone = raw_customer.get("phone_number")
        address = raw_customer.get("address", {})
        customer.address1 = address.get("address_line_1", "")
        customer.city = address.get("locality", "")
        customer.zip_code = address.get("postal_code", "")
        customer.country = address.get("country", "")
        customer.state = address.get("administrative_district_level_1", "")
        customer.save()

    @staticmethod
    def delete_customer(retailer, payload):
        origin_id = payload['customer']['id']
        retailer.customers.filter(origin_id=origin_id).delete()

    @staticmethod
    def fetch_all_customers(retailer):
        if not retailer.access_token:
            logger.error(f"Access token not found for retailer: {retailer.merchant_id}")
            return

        client = SquareRequestClient(retailer.access_token)
        try:
            list_response = client.list_customers()
        except Exception as e:
            # TODO: Send email to admin with the error
            logger.error(f"Error Loading customer for Square, retailer id {retailer.id}, exception", e)
            return

        customers = list_response.get('customers', [])
        for customer in customers:
            try:
                SquareCustomer.store(customer, retailer)
            except Exception as e:
                logger.error(f"Error parsing customer {customer['id']} for Square,"
                             f" retailer id {retailer.id}, exception {e}")
