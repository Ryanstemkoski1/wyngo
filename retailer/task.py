import logging
from datetime import datetime, timedelta

from django.template.loader import render_to_string
from django.utils import timezone

from common.pos.square.square_oauth import SquareOauth
from retailer.models import Retailer
from wyndo.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def refresh_token_task(self):
    logger.info("Starting refresh token task")
    base_query = Retailer.objects.filter(origin=Retailer.SQUARE).filter(
        refresh_token__isnull=False
    )

    logger.info("Disconnecting retailers that are already expired")
    time_check = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
    retailers_expired = base_query.filter(expires_at__lte=time_check)
    for retailer in retailers_expired:
        retailer.disconnect_retailer()

    logger.info("Refreshing tokens with 8 or more days old")
    retailers = base_query.filter(
        token_created_at__lte=time_check - timedelta(days=8),
        expires_at__gt=time_check,
    )
    for retailer in retailers:
        SquareOauth.refresh_oauth_session(retailer=retailer)

    logger.info("End refresh token task")

@app.task()
def denied_retailer_email(email, business_name, note):
    try:
        message = render_to_string(
            "email_template_denied_retailer.html",
            {
                "business_name": business_name,
                "note": note,
            },
        )
        Retailer.send_email(message, email, "Application denied")
    except Exception as e:
        logging.error(str(e))