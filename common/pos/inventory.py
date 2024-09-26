from abc import ABC, abstractmethod
from time import time

from common.goupc import GoUPC
from inventories.models import Inventory as IventoryModel
from inventories.models import Product as ProductModel
from inventories.models import Variant as VariantModel
from inventories.models import VariantImage as VariantImageModel
from retailer.models import Retailer


class AbstractInventory(ABC):
    def __init__(self, retailer):
        self._inventory = None
        self._retailer: Retailer = retailer

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def get_or_create_inventories(self):
        pass

    @abstractmethod
    def update_or_create_product(self, data):
        pass

    @abstractmethod
    def update_or_create_variant(self, data, product):
        pass

    @abstractmethod
    def update_or_create_variant_image(self, data):
        pass

    @abstractmethod
    def store(self, products):
        pass

    @abstractmethod
    def process(self, products):
        pass

    @abstractmethod
    def run(self, item_id: str = None):
        pass

    @abstractmethod
    def delete_product(self, origin_id: str, inventory: IventoryModel):
        pass

    @abstractmethod
    def create_pos_item(self, product):
        pass

    @abstractmethod
    def update_pos_item(self, product, form, formset):
        pass

    @abstractmethod
    def delete_pos_product(self, product):
        pass


class Inventory(AbstractInventory):
    def __init__(self, retailer):
        super().__init__(retailer)
        self._go_upc_client = GoUPC()

    def get_or_create_inventories(self):
        location = self._retailer.location_set.first()
        inventory = IventoryModel.objects.filter(location=location).first()

        if inventory is None:
            # Creating the inventory for the retailer
            inventory_name = f"{self._retailer.name}-{int(time())}"
            inventory = IventoryModel.objects.create(
                name=inventory_name, location=location
            )

        return inventory

    def update_or_create_product(self, data):
        product_filter = {
            "origin_id": data["origin_id"],
            "inventory": data["inventory"],
        }

        products = ProductModel.objects.filter(**product_filter)
        if products.exists():
            data.pop("inventory", None)
            # count element that has sync flag active to avoid reload name (PENDING TO VALIDATE)

        product, created = ProductModel.objects.update_or_create(
            defaults=data, **product_filter
        )

        return product

    def update_or_create_variant(self, data, product):
        variant, created = VariantModel.objects.update_or_create(
            origin_id=data.get("origin_id"), defaults=data, product=product
        )
        return variant

    def update_or_create_variant_image(self, data):
        exist = VariantImageModel.objects.filter(image_id=data["image_id"]).exists()
        if not exist:
            VariantImageModel.objects.update_or_create(
                image_id=data.get("image_id"), defaults=data
            )

    def delete_product(self, origin_id: str, inventory: IventoryModel):
        # TODO: Delete products and variants logically
        product = ProductModel.objects.filter(origin_id=origin_id, inventory=inventory)
        if product.exists():
            product.delete()
        else:
            variant = VariantModel.objects.filter(origin_id=origin_id)

            products = ProductModel.objects.get(variants__in=variant)
            if variant.exists():
                variant.delete()
                if products.variants.count() == 0:
                    products.delete()
