import copy
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlencode

from django.conf import settings
from django.urls import reverse
from requests import Response, get, post

from retailer.models import Retailer

logger = logging.getLogger(__name__)


class CloverOauth:
    @staticmethod
    def create_clover_oauth_path(retailer: Retailer, request) -> str:
        oauth_url = urljoin(settings.CLOVER_URL, settings.CLOVER_OAUTH_PATH)
        query_params = {
            "client_id": retailer.app_id,
            "redirect_uri": request.build_absolute_uri(reverse("clover_callback", args=[retailer.id])),
        }
        encoded_query_params = urlencode(query_params)
        return f"{oauth_url}?{encoded_query_params}"

    @staticmethod
    def run_health_check(access_token, merchant_id) -> bool:
        get_merchant_url = urljoin(
            settings.CLOVER_URL, settings.CLOVER_MERCHANT_INFO_PATH
        ).format(mId=merchant_id)

        headers = copy.deepcopy(settings.CLOVER_HEADERS)
        headers["authorization"] = headers.get("authorization").format(
            bearer_token=access_token
        )

        response: Response = get(url=get_merchant_url, headers=headers)

        return response.status_code == 200

    @staticmethod
    def create_oauth_session(merchant_id: str, app_id: str, code: str, retailer_id: int) -> dict:
        retailer = Retailer.objects.get(id=retailer_id, app_id=app_id)

        if code is None or not bool(code):
            # TODO: Send email to admin with the error
            logger.error(
                "Error processing the request, the code %s is either null or invalid"
            )
            return {
                "status": -1,
                "message": "Error processing the request: Invalid Clover response",
            }

        oauth_request_body: dict = {
            "client_id": app_id,
            "client_secret": retailer.app_secret,
            "code": code,
        }
        token_url = urljoin(settings.CLOVER_URL, settings.CLOVER_TOKEN_PATH)
        url = f"{token_url}?{urlencode(oauth_request_body)}"

        response: Response = post(url=url, json=oauth_request_body, headers={"accept": "application/json"})

        if response.status_code != 200:
            return {
                "status": -1,
                "message": "Error processing the request: Invalid Clover response",
            }
        oauth_response_body = response.json()

        if not CloverOauth.run_health_check(
            access_token=oauth_response_body["access_token"], merchant_id=merchant_id
        ):
            return {
                "status": -2,
                "message": "Error processing the request: Invalid Clover status response",
            }
        retailer.merchant_id = merchant_id
        retailer.access_token = oauth_response_body["access_token"]
        retailer.token_type = "Bearer"
        retailer.token_created_at = datetime.now()
        retailer.expires_at = datetime.now() + timedelta(days=364)
        retailer.save()

        return {
            "status": 0,
            "message": "Successful connection",
            "retailer_id": retailer.id,
        }
