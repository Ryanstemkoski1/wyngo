from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from accounts.models import User
from inventories.models import Inventory
from retailer.models import Location, Retailer


class RetailerUtils:
    @staticmethod
    def create_retailer_permission_group():
        group_name = settings.RETAILER_PERMISSION_GROUP_NAME
        permission_data = settings.RETAILER_PERMISSION_GROUP_DATA
        group_obj, is_created = Group.objects.get_or_create(name=group_name)
        group_obj.permissions.clear()

        current_permissions = list(group_obj.permissions.all())
        for item in permission_data:
            content_type = ContentType.objects.filter(app_label=item["app_label"], model=item["model"]).first()
            if not content_type:
                continue
            for code_name in item["codes"]:
                permission_obj = Permission.objects.filter(content_type=content_type, codename=code_name).first()
                if permission_obj:
                    group_obj.permissions.add(permission_obj)
                    if permission_obj in current_permissions:
                        current_permissions.remove(permission_obj)
        # TODO: Consider to keep or remove remaining permissions that do not exist on permission_data

    @staticmethod
    def get_retailer_locations(retailer_email):
        return Location.objects.filter(
            retailer__email=retailer_email,
            retailer__status=Retailer.STATUS_APPROVED
        )

    @staticmethod
    def get_retailer_inventories(retailer_email):
        return Inventory.objects.filter(
            location__in=Location.objects.filter(
                retailer__email=retailer_email,
                retailer__status=Retailer.STATUS_APPROVED
            )
        )

    @staticmethod
    def check_and_promote_retailer_admin_account(retailer_email):
        retailer_staff = User.objects.filter(email=retailer_email).first()
        if retailer_staff:
            retailer_group = Group.objects.filter(name=settings.RETAILER_PERMISSION_GROUP_NAME).first()
            if retailer_group:
                retailer_staff.groups.add(retailer_group)
            if not retailer_staff.is_staff:
                retailer_staff.is_staff = True
                retailer_staff.save()
