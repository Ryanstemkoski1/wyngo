import logging
import re
from os import getenv

import requests
from django.core.files.base import ContentFile

from inventories.models import Product

logger = logging.getLogger(__name__)


class GoUPC:
    def __init__(self):
        self._api_key = getenv("GO_UPC_KEY", "")
        self._url = getenv("GO_UPC_URL", "")

    def get_product_image_from_url(self, url, code):
        response = requests.get(url)
        img_file = None
        img_name = re.split(r"/", url)[-1]
        img_ext = re.split("\.", img_name)
        img_ext[0] = code
        img_name = ".".join(img_ext)
        if response.status_code == 200:
            img_file = ContentFile(response.content, name=img_name)
        return img_name, img_file

    def create_product(self, code, retailer):
        response = requests.get(f"{self._url}/{code}?key={self._api_key}")
        if response.status_code != 200:
            raise ValueError("Problem API call go upc")
        data = response.json()
        product = data.get("product")

        Product.objects.create(
            sku=data.get("code"),
            upc=data.get("code"),
            product_title=product.get("name"),
            quantity=0,
            price=0,
            image=self.get_product_image_from_url(
                product.get("imageUrl"), data.get("code")
            ),
            retailer=retailer,
        )

    def get_product_information(self, code: str) -> dict:
        if not self._api_key or not self._url:
            return {}

        headers = {"Authorization": f"Bearer {self._api_key}"}
        response = requests.get(f"{self._url}/{code}", headers=headers)

        if response.status_code != 200:
            logger.error(f"URL: {self._url}")
            logger.error(f"Bearer {self._api_key}")
            logger.error(f"UPC: {code}")
            logger.error("Error fetching data from GoUPC")
            logger.error("status_code %s", response.status_code)
            return {}

        print("Success fetching go upc")

        data = response.json()
        product = data.get("product")
        return product
