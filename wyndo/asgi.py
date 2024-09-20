"""
ASGI config for wyndo project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from common.retailer_utils import RetailerUtils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wyndo.settings')

application = get_asgi_application()
# Create retail permission group
RetailerUtils.create_retailer_permission_group()
