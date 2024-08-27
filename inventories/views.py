import json
import logging
from http import HTTPStatus

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.pos.clover.clover_webhook import CloverWebhook
from common.pos.square.square_webhook import SquareWebhook
from .models import VariantImage

logger = logging.getLogger(__name__)


@csrf_exempt
def delete_image(request, image_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "method not allowed"}, status=405)

    try:
        image = VariantImage.objects.get(id=image_id)
        image.delete()
        return JsonResponse({"success": True})
    except VariantImage.DoesNotExist:
        return JsonResponse({"error": "image not found"}, status=404)


@csrf_exempt
def webhook_clover_events(request):
    webhook_service = CloverWebhook()
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method Not Allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED
        )

    request_body = json.loads(request.body)

    if request_body.get("verificationCode") is not None:
        try:
            if webhook_service.send_verification_email(
                request_body.get("verificationCode")
            ):
                return JsonResponse({"success": True}, status=HTTPStatus.OK)
            return JsonResponse(
                {"success": False}, status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            # TODO: Send superuser an email to report the problem
            logger.error(
                "Error processing Clover webhook verification code event, exception: ",
                e,
            )
            return JsonResponse(
                {"success": False}, status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

    try:
        webhook_service.process_events(body=request_body)
    except KeyError as e:
        logger.error("Error processing Clover request body, exception: ", e)
        return JsonResponse({"success": False}, status=HTTPStatus.BAD_REQUEST)
    except Exception as e:
        logger.error("Error processing Clover webhook event, exception: ", e)
        return JsonResponse({"success": False}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return JsonResponse({"success": True}, status=HTTPStatus.OK)


@csrf_exempt
def webhook_square_event(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Method Not Allowed"}, status=HTTPStatus.METHOD_NOT_ALLOWED
        )

    request_body = json.loads(request.body)

    event_type = request_body["type"]
    event_id = request_body["event_id"]
    merchant_id = request_body["merchant_id"]

    cached_trace = json.loads(cache.get(f"{merchant_id}_{event_id}", "{}"))

    if len(cached_trace) != 0:
        if (
            cached_trace["event_id"] == event_id
            and cached_trace["event_type"] == event_type
            and cached_trace["status"] == "PROCESS"
        ):
            return JsonResponse(
                {"success": False, "message": "Event was queued previously"},
                status=HTTPStatus.TOO_EARLY,
            )
        elif (
            cached_trace["event_id"] == event_id
            and cached_trace["event_type"] == event_type
            and cached_trace["status"] == "SUCCESS"
        ):
            return JsonResponse(
                {"success": True},
                status=HTTPStatus.OK,
            )

    webhook_service = SquareWebhook()
    webhook_service.process_events(
        merchant_id=merchant_id,
        event_id=event_id,
        event_type=event_type,
        body=request_body.get("data").get("object"),
    )

    return JsonResponse({"success": True}, status=HTTPStatus.OK)
