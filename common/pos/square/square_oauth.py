import logging
import uuid
from datetime import datetime
from urllib.parse import urljoin, urlencode

from dateutil import parser
from django.conf import settings
from square.client import Client
from square.http.api_response import ApiResponse

from retailer.models import Retailer

logger = logging.getLogger(__name__)


class SquareOauth:
    @staticmethod
    def create_square_oauth_path(retailer: Retailer):
        # if there's a valid refresh token, it authenticates with that flow
        if retailer.refresh_token is not None and retailer.is_access_token_expired():
            return "refresh_token"

        csrf: str = uuid.uuid4().__str__().replace("-", "")
        retailer.square_csrf = csrf
        retailer.save()
        permissions: str = (
            "ITEMS_READ ITEMS_WRITE ORDERS_WRITE ORDERS_READ CUSTOMERS_WRITE CUSTOMERS_READ"
            " INVENTORY_READ INVENTORY_WRITE INVOICES_READ INVOICES_WRITE MERCHANT_PROFILE_READ"
        )
        login_url = urljoin(settings.SQUARE_URL, settings.SQUARE_OAUTH_PATH)
        query_params = {
            "client_id": retailer.app_id,
            "scope": permissions,
            "session": "false",
            "state": csrf,
        }
        encoded_query_params = urlencode(query_params)

        return f"{login_url}?{encoded_query_params}"

    @staticmethod
    def run_health_check(access_token) -> bool:
        client: Client = Client(
            access_token=access_token, environment=settings.SQUARE_ENVIRONMENT
        )
        health_check_response: ApiResponse = client.o_auth.retrieve_token_status(
            f"Bearer {access_token}"
        )
        return health_check_response.is_success()

    @staticmethod
    def create_oauth_session(state: str, code: str) -> dict:
        retailer: Retailer = Retailer.objects.get(square_csrf=state)

        if not bool(code):
            # TODO: Send email to admin with the error
            logger.error(
                "Error processing the request, the code %s is either null or invalid"
            )
            return {
                "status": -1,
                "message": "Error processing the request: Invalid Square response",
            }

        client: Client = Client(environment=settings.SQUARE_ENVIRONMENT)
        oauth_response_body: ApiResponse = client.o_auth.obtain_token(
            body={
                "client_id": retailer.app_id,
                "client_secret": retailer.app_secret,
                "code": code,
                "grant_type": "authorization_code",
            }
        )
        if oauth_response_body.is_error():
            return {
                "status": -3,
                "message": "Error processing the request: Invalid Square Token response",
            }

        if not SquareOauth.run_health_check(
            access_token=oauth_response_body.body["access_token"]
        ):
            return {
                "status": -2,
                "message": "Error processing the request: Invalid Square status response",
            }

        retailer.access_token = oauth_response_body.body["access_token"]
        retailer.token_created_at = datetime.now()
        retailer.expires_at = oauth_response_body.body["expires_at"]
        retailer.refresh_token = oauth_response_body.body["refresh_token"]
        retailer.token_type = oauth_response_body.body["token_type"]
        retailer.square_csrf = None
        retailer.save()

        return {
            "status": 0,
            "message": "Successful connection",
            "retailer_id": retailer.id,
        }

    @staticmethod
    def refresh_oauth_session(retailer: Retailer) -> dict:
        client = Client(environment=settings.SQUARE_ENVIRONMENT)
        oauth_response_body: ApiResponse = client.o_auth.obtain_token(
            body={
                "client_id": retailer.app_id,
                "client_secret": retailer.app_secret,
                "refresh_token": retailer.refresh_token,
                "grant_type": "refresh_token",
            }
        )

        if not SquareOauth.run_health_check(
            access_token=oauth_response_body.body["access_token"]
        ):
            return {
                "status": -2,
                "message": "Error processing the request: Invalid Square status response",
            }

        retailer.access_token = oauth_response_body.body["access_token"]
        retailer.token_created_at = datetime.now()
        retailer.expires_at = parser.parse(oauth_response_body.body["expires_at"])
        retailer.refresh_token = oauth_response_body.body["refresh_token"]
        retailer.token_type = oauth_response_body.body["token_type"]
        retailer.save()

        return {
            "status": 0,
            "message": "Successful connection",
            "retailer_id": retailer.id,
        }
