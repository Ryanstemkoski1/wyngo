from django.apps import AppConfig


class RetailerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'retailer'

    def ready(self):
        try:
            from common.retailer_utils import RetailerUtils
            RetailerUtils.create_retailer_permission_group()
        except Exception as e:
            print(e)
