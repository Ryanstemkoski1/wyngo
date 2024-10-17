import logging
from urllib.parse import urlencode

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html

from . import views
from .forms import RetailerForm
from .models import Retailer, Category, ShoppingCenter, Location
from .task import denied_retailer_email


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0
    readonly_fields = (
        "name",
        "address1",
        "address2",
        "address3",
        "city",
        "country",
        "state",
        "zip_code",
        "pos_id",
    )

    def has_add_permission(self, request, _):
        return False

    class Media:
        css = {"all": ("css/admin/admin.css",)}


@admin.register(Retailer)
class RetailerAdmin(admin.ModelAdmin):
    exclude = (
        "access_token",
        "refresh_token",
        "app_id",
        "app_secret",
        "token_type",
        "expires_at",
        "square_csrf",
        "is_sync",
    )
    list_display = (
        "id",
        "name",
        "origin",
        "created_at",
        "updated_at",
        "status",
        "connected",
        "action_retailer_buttons",
    )
    list_display_links = ("name",)
    form = RetailerForm

    inlines = [LocationInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "approve_retailer/",
                self.admin_site.admin_view(views.approve_retailer),
                name="approve_retailer",
            ),
            path(
                "deny_retailer/",
                self.admin_site.admin_view(self.deny_retailer),
                name="deny_retailer",
            )
        ]
        return custom_urls + urls

    def deny_retailer(self, request):
        try:
            if request.method == 'POST':
                retailer_id: str = request.POST.get("id")
                retailer = Retailer.objects.get(pk=retailer_id)
                retailer.note = request.POST.get('note')
                retailer.status = Retailer.STATUS_DENIED
                retailer.save()
                denied_retailer_email.delay(
                    retailer.email, retailer.name, retailer.note
                )
                return redirect("admin:retailer_retailer_changelist")
            retailer_id: str = request.GET.get("i")
            retailer = Retailer.objects.get(pk=retailer_id)
            if retailer.status != Retailer.STATUS_REQUESTING:
                return redirect("admin:retailer_retailer_changelist")
            context = self.admin_site.each_context(request)
            context['retailer'] = retailer
            return TemplateResponse(request, "deny_retailer.html", context)
        except Exception as ex:
            logging.exception(f'deny_retailer with ex={ex}')
        return redirect("admin:retailer_retailer_changelist")
    
    def action_retailer_buttons(self, obj: Retailer):
        encoded_query_params = urlencode({"i": obj.pk})
        approve_url = f"{reverse('admin:approve_retailer')}?{encoded_query_params}"
        deny_url = f"{reverse('admin:deny_retailer')}?{encoded_query_params}"
        action_buttons = (
            "<a href='{}' style='padding-right: 10px;'><button id='btn_deny' type='button' class='button'>Deny</button></a>"
            "<a href='{}'><button id='btn_approve' type='button' class='button'>Approve</button></a>"
            if obj.status == Retailer.STATUS_REQUESTING
            else ""
        )
        disabled_button = ""
        return format_html(action_buttons, deny_url, approve_url)

    def connected(self, obj: Retailer):
        if obj.expires_at is None:
            return False
        return not obj.is_access_token_expired()

    action_retailer_buttons.short_description = "Actions"
    action_retailer_buttons.allow_tags = True

    connected.boolean = True
    connected.sortable_by = True
    connected.ordering = True

    def get_changeform_initial_data(self, request):
        get_data = super().get_changeform_initial_data(request)
        get_data["user"] = request.user.pk
        return get_data

    def get_queryset(self, request):
        queryset = super(RetailerAdmin, self).get_queryset(request)

        if request.user.is_superuser:
            return queryset

        return queryset.filter(user=request.user)

    def save_form(self, request, form, change):
        if "merchant_id" in form.changed_data:
            messages.warning(request, "By doing this you must connect again to the POS")
        return form.save(commit=False)
        # return super().save_form(request, form, change)

    class Media:
        css = {
            "all": (
                "css/admin/sweetalert2.css",
                "css/admin/iconsgoogle.css",
            )
        }
        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/retailers.js",
            "js/admin/sweetalert2.min.js",
        )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")

    class Media:
        css = {"all": ("css/admin/iconsgoogle.css",)}

        js = (
            "js/admin/jquery-3.3.1.min.js",
            "js/admin/categories.js",
        )


@admin.register(ShoppingCenter)
class ShoppingCenterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
