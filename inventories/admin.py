from datetime import timedelta

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.db.models import Q, QuerySet
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.urls import path
from django.utils.html import format_html
from django_admin_inline_paginator.admin import TabularInlinePaginated
from rangefilter.filters import DateRangeFilter

from common.filters import PriceRangeFilter
from common.pos.clover import CloverInventory
from common.retailer_utils import RetailerUtils
from retailer.models import Retailer
from .forms import CategoryForm, ProductForm, VariantForm
from .models import Category, Product, Variant, Inventory, Reservation, Customer, ReservationItem, ReservationPickup


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = (
        "name",
        ("created_at", DateRangeFilter),
    )
    list_display = ("name", "created_at")
    form = CategoryForm

    class Media:
        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/filter_validation.js",
        )


class VariantInline(admin.TabularInline):
    model = Variant
    form = VariantForm
    verbose_name = "Variation"
    verbose_name_plural = "Variations"
    extra = 0
    exclude = ("currency", "origin_id", "origin_parent_id")
    readonly_fields = (
        "display_images",
    )
    fields = (
        "name",
        "price",
        "sku",
        "upc",
        "stock",
        "image",
        "display_images",
        "description",
        "is_modified_by_admin",
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def display_images(self, obj):
        images = obj.get_images()
        return format_html(
            "<br>".join(
                [
                    f'<a href="{image.image.url}" target="_blank">View image #{i + 1}</a>'
                    #<a href="#" class="delete-image"><span class="material-symbols-outlined delete-red" data-image-id="{image.id}">highlight_off</span></a>
                    for i, image in enumerate(images)
                ]
            )
        )

    display_images.short_description = "Images"

    def has_add_permission(self, request, _):
        return False

    class Media:
        css = {"all": ("css/admin/admin.css", "css/admin/iconsgoogle.css")}

        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/variant.js",
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    actions = None
    list_filter = (
        "origin",
        PriceRangeFilter,
        ("created_at", DateRangeFilter),
    )
    inlines = [VariantInline]
    form = ProductForm
    list_display = (
        "name",
        "category",
        "is_active",
        "min_price",
        "max_price",
        "inventory",
        "get_variations",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "name",
        "category",
        "origin",
        "origin_id",
        "min_price",
        "inventory",
        "max_price",
        "total_stock",
        "is_modified_by_admin",
    )
    fields = (
        "is_active",
        "name",
        "category",
        "origin",
        "origin_id",
        "min_price",
        "inventory",
        "max_price",
        "total_stock",
        "is_modified_by_admin",
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProductAdmin, self).get_form(request, obj, **kwargs)
        # if request.user.is_superuser:
        #     inventory_qs = Inventory.objects.all()
        # else:
        #     inventory_qs = Inventory.objects.filter(
        #         location__retailer__email=request.user.email
        #     )
        # form.base_fields['inventory'].queryset = inventory_qs
        return form

    def get_variations(self, obj):
        return obj.variants.count()

    get_variations.short_description = "Variations"

    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(inventory__in=RetailerUtils.get_retailer_inventories(request.user.email))
        return qs

    # def save_model(self, request, obj, form, change):
    #     pass  # don't actually save the parent instance
    #
    # def save_formset(self, request, form, formset, change):
    #     formset.save()  # this will save the children
    #     form.instance.save()  # form.instance is the parent
    #
    #     retailer = Retailer.objects.filter(
    #         email=request.user.email,
    #         origin=form.instance.origin,
    #     ).first()
    #     if not retailer:
    #         return
    #     if form.instance.origin == Product.SQUARE:
    #         return  # Not supported SQUARE yet
    #
    #     pos_instance = CloverInventory(retailer)
    #     if change:
    #         pos_instance.update_pos_item(form.instance, form, formset)
    #     else:
    #         pos_instance.create_pos_item(form.instance)
    #
    # def delete_model(self, request, obj):
    #     retailer = Retailer.objects.filter(
    #         email=request.user.email,
    #         origin=obj.origin,
    #     ).first()
    #     if not retailer:
    #         return
    #     if obj.origin == Product.SQUARE:
    #         return  # Not supported SQUARE yet
    #
    #     pos_instance = CloverInventory(retailer)
    #     pos_instance.delete_pos_product(obj)
    #     super().delete_model(request, obj)

    # def _clean_variant_name(self, product):
    #     product_name = product.name
    #     for variant in product.variants.all():
    #         variant_name = variant.name
    #         _variant_name = variant_name.replace(product_name, "") \
    #             if variant_name.startswith(product_name) else variant_name
    #         variant.name = _variant_name
    #         variant.save()
    #     product.save()


    class Media:
        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/filter_validation.js",
        )


class ProductInline(TabularInlinePaginated):
    per_page = 10
    model = Product
    extra = 0
    exclude = ("origin_id",)
    readonly_fields = (
        "name",
        "min_price",
        "max_price",
        "category",
        "total_stock",
        "created_at",
        "updated_at",
    )
    show_change_link = True
    fields = ("name", "category", "min_price", "max_price", "created_at", "updated_at")

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    class Media:
        css = {"all": ("css/admin/admin.css",)}


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = (
        "name",
        ("created_at", DateRangeFilter),
    )
    inlines = [ProductInline]
    readonly_fields = (
        "name",
        "location",
    )
    list_display = ("name", "get_retailers", "created_at")

    def get_retailers(self, obj):
        return obj.location.retailer if obj is not None else ""

    get_retailers.short_description = "Retailer's Name"

    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(location__in=RetailerUtils.get_retailer_locations(request.user.email))
        return qs.filter(location__retailer__status=Retailer.STATUS_APPROVED)

    class Media:
        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/filter_validation.js",
        )


class RetailerFilter(AutocompleteFilter):
    title = "Retailer"
    field_name = "user"


class ReservationItemInline(admin.TabularInline):
    model = ReservationItem
    extra = 0
    verbose_name = "Reservation Item"
    verbose_name_plural = "Reservation Items"
    readonly_fields = (
        "order_time",
    )
    fields = (
        "variant",
        "quantity",
        "unit_price",
        "variation_total",
        "tax",
        "total_price",
        "order_time",
    )


    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    can_delete = False


class ReservationPickupInline(admin.TabularInline):
    model = ReservationPickup
    extra = 0
    verbose_name = "Pickup"
    verbose_name_plural = "Pickups"

    exclude = ("origin_id",)
    readonly_fields = (
        "location",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_filter = (
        ("order_time", DateRangeFilter),
        ("updated_at", DateRangeFilter),
        "status",
    )
    readonly_fields = (
        "total",
        "status",
        "reservation_code",
        "updated_at",
        "created_at",
    )
    list_display = (
        "reservation_code",
        "total",
        "currency",
        "quantity",
        "status",
        "customer",
        "order_time",
        "retailer",
    )
    search_fields = (
        "origin_id",
        "origin",
        "total",
        "status",
        "quantity",
        "reservation_code",
        "variant__name",
        "user__email",
    )

    fields = (
        "reservation_code",
        "customer",
        "quantity",
        "order_time",
        "status",
        "currency",
        "subtotal",
        "tax",
        "total",
        "retailer",
        "updated_at",
    )

    inlines = [ReservationPickupInline, ReservationItemInline]


    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(retailer__email=request.user.email)
        return qs

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        if search_term:
            try:
                search_term = str(search_term).strip()
            except ValueError:
                pass
            else:
                queryset |= self.model.objects.annotate(
                    full_name=Concat("user__first_name", V(" "), "user__last_name")
                ).filter(full_name__icontains=search_term)
        return queryset, may_have_duplicates

    def get_full_name(self, obj):
        if not obj.user:
            return ""
        return (f"{obj.user.first_name} {obj.user.last_name}",)

    get_full_name.short_description = "Full Name"

    @staticmethod
    def convert_string_to_date(start_date):
        from datetime import datetime

        try:
            date_time_obj = datetime.strptime(start_date, "%d/%m/%Y")
        except Exception as e:
            date_time_obj = datetime.strptime(start_date, "%Y-%m-%d")
        return date_time_obj

    def get_urls(self):
        urls = super(ReservationAdmin, self).get_urls()
        custom_urls = [
            path(
                "emit/",
                self.admin_site.admin_view(self.report_service),
                name="report-export-reservation",
            ),
        ]

        return custom_urls + urls

    def report_service(self, request, *args, **kwargs):
        qfilter = Q(id__isnull=False)
        created_at_range_gte = request.GET.get("order_time__range__gte")
        created_at_range_lte = request.GET.get("order_time__range__lte")
        retailer = request.GET.get(
            "retailer__id__exact"
        )
        status = request.GET.get("status")

        if retailer:
            qfilter.add(
                Q(
                    retailer__id__exact=int(
                        retailer
                    ),
                ),
                qfilter.connector,
            )

        if status:
            qfilter.add(
                Q(
                    status=status,
                ),
                qfilter.connector,
            )

        if created_at_range_lte and created_at_range_gte:
            created_at_range_gte = ReservationAdmin.convert_string_to_date(
                created_at_range_gte
            )
            created_at_range_lte = ReservationAdmin.convert_string_to_date(
                created_at_range_lte
            )

            created_at_range_lte = created_at_range_lte + timedelta(days=1)

            qfilter.add(
                Q(
                    created_at__gte=created_at_range_gte,
                    created_at__lte=created_at_range_lte,
                ),
                qfilter.connector,
            )

        stocks = Reservation.objects.filter(qfilter).order_by("-id")
        if not request.user.is_superuser:
            stocks = stocks.filter(retailer__email=request.user.email)
        return Reservation.generate_report_csv(
            stocks, created_at_range_gte, created_at_range_lte
        )

    class Media:
        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/filter_validation.js",
        )


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0

    fields = (
        'reservation_code',
        'status',
        'total',
        'currency',
        'quantity',
        'order_time',
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = ("email", "first_name", "last_name", "phone", "city", "state", "country")
    list_filter = ("city", "state", "country")
    search_fields = ("email", "first_name", "last_name", "phone",)
    exclude = ("origin_id",)

    inlines = [ReservationInline]

    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(retailer=Retailer.objects.get(email=request.user.email))
        return qs
