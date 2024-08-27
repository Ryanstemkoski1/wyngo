from django import template
from django.db.models import Sum
from django.utils import timezone

from inventories.models import Product, Reservation as ReservationModel, Variant

register = template.Library()


@register.filter
def minutes_until_datetime(datetime_field):
    try:
        current_time = timezone.now()

        time_difference = datetime_field - current_time

        minutes_left = time_difference.total_seconds() / 60
        seconds_left = time_difference.total_seconds() % 60

        return f"{int(minutes_left)}m {int(seconds_left)}s"
    except (ValueError, TypeError):
        return None


@register.filter
def calculate_reliability_score(product):
    stock = 0
    variants = []

    if isinstance(product, Variant):
        stock = product.stock
        variants.append(product.id)

    elif isinstance(product, Product):
        stock = product.total_stock
        variants = Variant.objects.filter(product=product).values_list(
            'id', flat=True)

    total_reserved = ReservationModel.objects.filter(
        variant_id__in=variants, status='RESERVED'
    ).aggregate(total=Sum('quantity')).get('total', None)

    if not total_reserved:
        return stock

    return stock - total_reserved
