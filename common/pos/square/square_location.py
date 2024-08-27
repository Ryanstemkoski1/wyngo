import logging

from django.conf import settings
from square.client import Client
from square.http.api_response import ApiResponse

from retailer.models import Retailer, Location

logger = logging.getLogger(__name__)


class SquareLocation:
    @staticmethod
    def fetch_locations(retailer_id: int):
        retailer = Retailer.objects.get(pk=retailer_id)
        retailer_locations = retailer.location_set.all()

        client = Client(
            environment=settings.SQUARE_ENVIRONMENT, access_token=retailer.access_token
        )
        try:
            locations_response: ApiResponse = client.locations.list_locations()
        except Exception as e:
            # TODO: Send email to admin with the error
            logger.error("Error connecting with Square, exception", e)
            return

        if locations_response.is_success():
            location_body = locations_response.body
            for pos_location in location_body["locations"]:
                location: Location = None
                for current_location in retailer_locations:
                    if current_location.pos_id == pos_location["id"]:
                        location = current_location

                if location is None:
                    location = Location()

                location_dict = {
                    "address1": pos_location["address"].get("address_line_1"),
                    "address2": pos_location["address"].get("address_line_2"),
                    "address3": pos_location["address"].get("address_line_3"),
                    "city": pos_location["address"].get("locality"),
                    "country": pos_location["address"].get("country"),
                    "state": pos_location["address"].get(
                        "administrative_district_level_1"
                    ),
                    "zip_code": pos_location["address"].get("postal_code"),
                    "pos_id": pos_location["id"],
                    "name": pos_location["name"],
                }

                location.update_location(**location_dict)
                location.retailer = retailer

                location.save()
                retailer.merchant_id = pos_location["merchant_id"]
                retailer.save()
            logger.info(f"Finished with {retailer_id}")
        elif locations_response.is_error():
            # TODO: Send email to admin with the error
            logger.error(
                "Square Location endpoint error, errors %s",
                locations_response.errors,
            )
            return

        else:
            # TODO: Send email to admin with the error
            logger.error(
                "Square Location endpoint error, errors %s",
                "Couldn't complete the request",
            )
            return

    @staticmethod
    def create_or_update_location(location_id: str, retailer: Retailer) -> dict:
        client = Client(
            environment=settings.SQUARE_ENVIRONMENT, access_token=retailer.access_token
        )

        try:
            locations_response: ApiResponse = client.locations.retrieve_location(
                location_id=location_id
            )
        except Exception as e:
            # TODO: Send email to admin with the error
            logger.error("Error connecting with Square, exception", e)
            return {"status": -1, "message": "Error connecting with Square"}

        if locations_response.is_error():
            logger.error(
                "Square Retrieve Location endpoint error", locations_response.errors
            )
            return {
                "status": -1,
                "message": "Square Retrieve Location endpoint error",
            }

        location_queryset = Location.objects.filter(
            pos_id=location_id, retailer=retailer
        )

        location = (
            location_queryset.first() if location_queryset.exists() else Location()
        )

        location_dict = {
            "address1": locations_response.body["location"]["address"].get(
                "address_line_1"
            ),
            "address2": locations_response.body["location"]["address"].get(
                "address_line_2"
            ),
            "address3": locations_response.body["location"]["address"].get(
                "address_line_3"
            ),
            "city": locations_response.body["location"]["address"].get("locality"),
            "country": locations_response.body["location"]["address"].get("country"),
            "state": locations_response.body["location"]["address"].get(
                "administrative_district_level_1"
            ),
            "zip_code": locations_response.body["location"]["address"].get(
                "postal_code"
            ),
            "pos_id": locations_response.body["location"]["id"],
            "name": locations_response.body["location"]["name"],
        }

        location.update_location(**location_dict)
        location.retailer = retailer

        location.save()
