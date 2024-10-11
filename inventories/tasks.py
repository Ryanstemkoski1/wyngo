import traceback

from celery import shared_task
from celery.utils.log import get_task_logger

from common.pos.clover import CloverInventory
from common.pos.clover.clover_customer import CloverCustomer
from common.pos.clover.clover_reservation import CloverReservation
from common.pos.square import SquareInventory
from common.pos.square.square_customer import SquareCustomer
from common.pos.square.square_reservation import SquareReservation
from retailer.models import Retailer
from wyndo.celery import app
from .models import Reservation

logger = get_task_logger(__name__)

INVENTORY_CLASSES = {Retailer.SQUARE: SquareInventory, Retailer.CLOVER: CloverInventory}


@app.task(bind=True)
def update_status_reservation(_, data: dict):
    Reservation.objects.filter(id=data.get("reservation")).update(
        status=data.get("status")
    )


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def load_clover_inventory(
    self, retailer_id: int = None, limit: int = 10, offset: int = 0
):
    logger.info(
        f"Starting Clover inventory loading process with parameters: retailer {retailer_id}, limit: {limit}, offset: {offset}"
    )
    try:
        if retailer_id is not None:
            retailers = Retailer.objects.filter(pk=retailer_id, status=Retailer.STATUS_APPROVED)
        else:
            retailers = (
                Retailer.objects.filter(origin=Retailer.CLOVER, is_sync=False, status=Retailer.STATUS_APPROVED)
                .exclude(access_token__isnull=True)
            )

        retailers = [
            retailer for retailer in retailers if not retailer.is_access_token_expired()
        ]

        if retailers:
            for retailer in retailers:
                retailer.update_sync(True)
                clover_inventory = CloverInventory(retailer, limit=limit, offset=offset)
                load_result = clover_inventory.run()
                retailer.update_sync(False)
                if load_result["result"] and load_result["fetch_next"]:
                    load_clover_inventory.delay(
                        retailer_id=load_result["retailer_id"],
                        limit=load_result["limit"],
                        offset=load_result["offset"],
                    )
                elif load_result["result"] and not load_result["fetch_next"]:
                    run_go_upc_integration.delay(retailer_id=retailer.pk)
    except Exception as exc:
        logger.error(f"Error loading Clover inventory: {str(exc)}")
        raise self.retry(exc=exc)
    finally:
        logger.info("Ended Clover inventory loading process")


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def load_square_inventory(self, retailer_id: int = None, cursor: str = None):
    logger.info(
        f"Starting Square inventory loading process with parameters: retailer {retailer_id}, cursor {cursor}"
    )
    try:
        if retailer_id is not None:
            retailers = Retailer.objects.filter(pk=retailer_id, status=Retailer.STATUS_APPROVED)
        else:
            retailers = (
                Retailer.objects.filter(origin=Retailer.SQUARE, status=Retailer.STATUS_APPROVED)
                .exclude(access_token__isnull=True)
            )

        retailers = [
            retailer for retailer in retailers if not retailer.is_access_token_expired()
        ]

        if retailers:
            for retailer in retailers:
                retailer.update_sync(True)
                square_inventory = SquareInventory(retailer, cursor=cursor)
                load_result = square_inventory.run()
                retailer.update_sync(False)
                if load_result["result"] and load_result["fetch_next"]:
                    load_square_inventory.delay(
                        retailer_id=load_result["retailer_id"],
                        cursor=load_result["cursor"],
                    )
                elif load_result["result"] and not load_result["fetch_next"]:
                    run_go_upc_integration.delay(retailer_id=retailer.pk)

    except Exception as exc:
        logger.error(f"Error loading Square inventory: {str(exc)}")
        raise self.retry(exc=exc)
    finally:
        logger.info("Ended Square inventory loading process")


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def process_square_catalog_event(self, body: dict, retailer_id: int = None):
    logger.info("Starting Square webhook catalog event")
    try:
        retailer = Retailer.objects.get(id=retailer_id)
        square_inventory = SquareInventory(retailer)
        square_inventory.run_webhook_update(body)
        run_go_upc_integration.delay(retailer_id=retailer.pk)
    except Exception as exc:
        logger.error(f"Error processing Square webhook catalog event: {str(exc)}")
        logger.error(exc, exc_info=True)
        raise self.retry(exc=exc)
    finally:
        logger.info("Ended Square webhook catalog event")


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def run_go_upc_integration(self, retailer_id: int = None):
    logger.info(
        f"Starting Go UPC integration process with parameters: retailer {retailer_id}"
    )
    try:
        if retailer_id is not None:
            retailers = Retailer.objects.filter(pk=retailer_id)
        else:
            retailers = Retailer.objects.filter(origin=Retailer.SQUARE).exclude(
                access_token__isnull=True
            )

        retailers = [
            retailer for retailer in retailers if not retailer.is_access_token_expired()
        ]

        if retailers:
            for retailer in retailers:
                inventory_class = INVENTORY_CLASSES.get(retailer.origin)
                if inventory_class:
                    inventory = inventory_class(retailer)
                    inventory.map_go_upc()
    except Exception as exc:
        logger.error(f"Error running Go UPC integration: {str(exc)}")
        raise self.retry(exc=exc)
    finally:
        logger.info("Ended Go UPC integration process")


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_square_customer(self, retailer_id: int = None):
    logger.info(f"[Celery] Fetching Square customers")
    retailers = Retailer.objects.filter(pk=retailer_id) \
        if retailer_id \
        else Retailer.objects.filter(origin=Retailer.SQUARE).exclude(access_token__isnull=True)

    for retailer in retailers:
        try:
            SquareCustomer.fetch_all_customers(retailer)
        except Exception as exc:
            logger.error(f"Error fetching Square customers: {str(exc)}")
            raise self.retry(exc=exc)
        finally:
            logger.info(f"[Celery] Ended fetching Square customers for retailer: {retailer.merchant_id}")


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_clover_customer(self, retailer_id: int = None):
    logger.info(f"[Celery] Fetching Clover customers")
    retailers = Retailer.objects.filter(pk=retailer_id) \
        if retailer_id \
        else Retailer.objects.filter(origin=Retailer.CLOVER).exclude(access_token__isnull=True)

    for retailer in retailers:
        try:
            CloverCustomer.fetch_all_customers(retailer)
        except Exception as exc:
            logger.error(f"Error fetching Clover customers: {str(exc)}")
            traceback.print_exc()
            raise self.retry(exc=exc)
        finally:
            logger.info(f"[Celery] Ended fetching Clover customers for retailer: {retailer.merchant_id}")


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_square_orders(self, retailer_id: int = None):
    logger.info(f"[Celery] Fetching Square orders")
    retailers = Retailer.objects.filter(pk=retailer_id) \
        if retailer_id \
        else Retailer.objects.filter(origin=Retailer.SQUARE).exclude(access_token__isnull=True)

    for retailer in retailers:
        try:
            square_reservation = SquareReservation(retailer)
            square_reservation.fetch_all_orders()
        except Exception as exc:
            logger.error(f"Error fetching Square orders: {str(exc)}")
            print(traceback.format_exc())
            raise self.retry(exc=exc)
        finally:
            logger.info(f"[Celery] Ended fetching Square orders for retailer: {retailer.merchant_id}")


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_clover_orders(self, retailer_id: int = None):
    logger.info(f"[Celery] Fetching Clover orders")
    retailers = Retailer.objects.filter(pk=retailer_id) \
        if retailer_id \
        else Retailer.objects.filter(origin=Retailer.CLOVER).exclude(access_token__isnull=True)

    for retailer in retailers:
        try:
            clover_reservation = CloverReservation(retailer)
            clover_reservation.fetch_all_orders()
        except Exception as exc:
            logger.error(f"Error fetching Clover orders: {str(exc)}")
            print(traceback.format_exc())
            raise self.retry(exc=exc)
        finally:
            logger.info(f"[Celery] Ended fetching Clover orders for retailer: {retailer.merchant_id}")
