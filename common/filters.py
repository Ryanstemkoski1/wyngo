from django.contrib import admin
from .forms import PriceRangeFilterForm


class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price'
    template = 'admin/price_range_filter.html'

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.request = request

    def lookups(self, request, model_admin):
        return (
            ('all', 'All'),
        )

    def queryset(self, request, queryset):
        min_price = request.GET.get('min_price__gte')
        max_price = request.GET.get('max_price__lte')

        if self.value() != 'all' and not max_price and not min_price:
            return queryset

        if min_price:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(max_price__lte=max_price)

        return queryset
