import copy
import logging
from urllib.parse import urljoin

from django.conf import settings
from requests import Response, get

from retailer.models import Retailer, Location

logger = logging.getLogger(__name__)


class CloverLocation:
    @staticmethod
    def fetch_locations(retailer_id: int = None, merchant_id: str = None):
        retailer = (
            Retailer.objects.get(pk=retailer_id)
            if retailer_id is not None
            else Retailer.objects.get(merchant_id=merchant_id)
        )
        retailer_locations = retailer.location_set.all()

        headers = copy.deepcopy(settings.CLOVER_HEADERS)
        headers["authorization"] = headers.get("authorization").format(
            bearer_token=retailer.access_token
        )
        location_url = urljoin(
            copy.deepcopy(settings.CLOVER_URL),
            copy.deepcopy(settings.CLOVER_LOCATION_PATH),
        ).format(mId=retailer.merchant_id)

        try:
            response: Response = get(url=location_url, headers=headers)
        except Exception as e:
            # TODO: Send email to admin with the error
            logger.error("Error connecting with Clover, exception", e)
            return

        if response.status_code != 200:
            # TODO: Send email to admin with the error
            logger.error(
                "Clover Address endpoint error, status code: %s, message: %s",
                response.status_code,
                response.json().get("message"),
            )
            return
        location_body = response.json()
        location_body["zip_code"] = location_body.get("zip")
        location_body.pop("href")
        location_body.pop("zip")

        if retailer_locations.count() == 0:
            location: Location = Location()
            location.update_location(**location_body)
            location.retailer = retailer

            location.save()
        else:
            for location in retailer_locations:
                location.update_location(**location_body)
                location.retailer = retailer

                location.save()
