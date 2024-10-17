import json
import logging
import traceback
from datetime import datetime

from django.core.paginator import Paginator
from django.db import transaction

from common.pos.repositories import (
    ProductRepository,
    VarianImageRepository,
    VariantRepository,
    InventoryRepository,
)
from common.pos.square.square_client import SquareRequestClient
from common.pos.utils import format_price
from inventories.models import Product, Variant, Category
from retailer.models import Retailer as RetailerModel
from .square_mapper import Item, ItemVariation, SquareInventoryMapper
from ...goupc import GoUPC


class SquareInventory:
    PLATFORM = "SQUARE"

    def __init__(self, retailer: RetailerModel, cursor: str = None):
        self._retailer = retailer
        self._go_upc_client = GoUPC()
        self.product_repository = ProductRepository()
        self.variant_repository = VariantRepository()
        self.inventory_repository = InventoryRepository()
        self.variant_image_repository = VarianImageRepository()
        self._request_client = SquareRequestClient(retailer.access_token)
        self._go_upc_client = GoUPC()
        self._cursor: str = cursor

    def fetch(self, updated_at: str = ""):
        request_client = SquareRequestClient(
            self._retailer.access_token, cursor=self._cursor
        )
        return (
            request_client.get_catalog()
            if not updated_at
            else request_client.search_catalog_by_date(updated_at=updated_at)
        )

    def get_locations(self):
        return self._retailer.location_set.all()

    def create_or_update_product(self, product: Item, location_id: str):
        inventory = self.inventory_repository.get_by_pos_id(location_id)
        product_obj = Product(
            origin=self.PLATFORM,
            origin_id=product.origin_id,
            name=product.name,
            inventory=inventory,
        )
        product = self.product_repository.update_or_create(product_obj)
        return product

    def create_or_update_variant(self, variant: ItemVariation, product: Product):
        variant_obj = Variant(
            origin_id=variant.origin_id,
            origin_parent_id=variant.origin_parent_id,
            name=variant.name,
            sku=variant.sku,
            upc=variant.upc,
            price=variant.price,
            currency=variant.currency,
            product=product,
        )
        return self.variant_repository.update_or_create(variant_obj)

    def update_variant_stock(
        self, retailer_id: str = "", origin_id: str = "", location_id: str = ""
    ):
        if retailer_id:
            variants = self.variant_repository.get_by_retailer_id(retailer_id)
            for variant in variants:
                stock = self._request_client.get_stock(
                    variant["origin_id"], variant["pos_id"]
                )
                if stock:
                    variant_stock = int(stock.get("counts", [])[0].get("quantity", 0))
                    self.variant_repository.update_stock(
                        variant_id=variant["id"], stock=variant_stock
                    )
        elif origin_id and location_id:
            stock = self._request_client.get_stock(origin_id, location_id)
            if stock:
                variant_stock = int(stock.get("counts", [])[0].get("quantity", 0))
                self.variant_repository.update_stock(
                    variant_origin_id=origin_id,
                    stock=variant_stock,
                    location_id=location_id,
                )

    def create_or_update_images(self, image, image_id, variant=None):
        self.variant_image_repository.update_or_create(
            {
                "variant": variant,
                "image": image,
                "image_id": image_id,
            }
        )

    def fetch_all_categories(self):
        categories = self._request_client.get_catalogs_by_type("CATEGORY")
        print(json.dumps(categories, indent=4))
        objects = categories.get("objects", [])
        for _object in objects:
            category = self.create_or_update_category(_object)

    def handle_categories_update(self, categories):
        for category in categories:
            self.create_or_update_category(category)

    def create_or_update_category(self, category_data: dict):
        _id = category_data.get("id")
        data = category_data.get("category_data", {})
        category, created = Category.objects.update_or_create(
            origin_id=_id,
            retailer=self._retailer,
            defaults={
                "name": data.get("name"),
            }
        )
        return category

    def retrieve_category_by_id(self, category_id):
        category = Category.objects.filter(origin_id=category_id, retailer=self._retailer).first()
        if not category:
            square_category = self._request_client.retrieve_catalog(category_id)
            category_data = square_category.get("object", {})
            category = self.create_or_update_category(category_data)
        return category

    def store(self, products: list[Item]):
        self.create_inventories()
        with transaction.atomic():
            for product in products:
                for location_id in product.locations:
                    self.create_or_update_product(product, location_id)

                for variant in product.variants:
                    for location_id in variant.locations:
                        logging.info(f"variant: {variant.name}")
                        logging.info(f"variant_location: {location_id}")
                        product_exists = self.product_repository.check_product_exists(
                            variant.origin_parent_id, location_id
                        )

                        for location in variant.location_overrides:
                            if location.get(
                                "location_id"
                            ) == location_id and location.get("price_money"):
                                variant.price = format_price(
                                    location.get("price_money").get("amount")
                                )

                        self.create_or_update_variant(variant, product_exists)

                    self._process_variant_category(variant, product)

                if len(product.variants) > 1:
                    self.product_repository.update_min_max_price(
                        self._retailer.id, product.origin_id
                    )

            self.update_variant_stock(retailer_id=self._retailer.id)

            self.product_repository.update_total_stock(self._retailer.id)

    def store_update(self, products: list[Item]):
        self.create_inventories()
        deleted_products = [product for product in products if product.is_deleted]

        with transaction.atomic():
            # Delete products in `deleted_products` list
            self.product_repository.delete_products(deleted_products)

            current_products = [
                product for product in products if not product.is_deleted
            ]
            for product in current_products:
                for location_id in product.locations:
                    self.create_or_update_product(product, location_id)
                for variant in product.variants:
                    for location_id in variant.locations:
                        product_exists = self.product_repository.check_product_exists(
                            variant.origin_parent_id, location_id
                        )
                        for location in variant.location_overrides:
                            if location.get(
                                "location_id"
                            ) == location_id and location.get("price_money"):
                                variant.price = format_price(
                                    location.get("price_money").get("amount")
                                )

                        self.create_or_update_variant(variant, product_exists)
                    self._process_variant_category(variant, product)
                variant_ids = [variant.origin_id for variant in product.variants]
                self.variant_repository.delete_missing_variants(
                    product=product, variant_ids=variant_ids
                )

                if len(product.variants) > 1:
                    self.product_repository.update_min_max_price(
                        self._retailer.id, product.origin_id
                    )

            self.update_variant_stock(retailer_id=self._retailer.id)

            self.product_repository.update_total_stock(self._retailer.id)

    def _process_variant_category(self, variant, product):
        variant_db = Variant.objects.filter(
            origin_id=variant.origin_id,
        ).first()
        variant_db.categories.clear()
        category_id = product.category_id
        category = None
        if category_id:
            category = self.retrieve_category_by_id(category_id)
        if category:
            category.variants.add(variant_db)
            category.save()

    def map_data(self, products):
        locations = self.get_locations()
        square_mapper = SquareInventoryMapper(products, locations)
        return square_mapper.get_mapped_data()

    @transaction.atomic
    def create_inventories(self):
        locations = self.get_locations()

        for location in locations:
            inventory = self.inventory_repository.get_by_location(location)
            if not inventory:
                self.inventory_repository.create(self._retailer.name, location)

    def process(self, data, update: bool = False):
        mapped_data = self.map_data(data)
        if not update:
            self.store(mapped_data)
        else:
            self.store_update(mapped_data)

    def run(self):
        try:
            data = self.fetch()
            cursor = data.get("cursor", None)
            if not data:
                return {"result": True, "fetch_next": False}

            print(json.dumps(data, indent=4))
            self.process(data)

            if cursor is not None:
                return {
                    "result": True,
                    "fetch_next": True,
                    "retailer_id": self._retailer.pk,
                    "cursor": cursor,
                }
            return {"result": True, "fetch_next": False}

        except Exception as e:
            traceback.print_exc()
            id = self._retailer.id
            logging.error(
                f"ERROR LOADING SQUARE INVENTORY for Retailer id {id}: {str(e)}"
            )
            return {"result": False, "fetch_next": False}

    def run_webhook_update(self, body: dict):
        try:
            updated_at = body.get("catalog_version", {}).get("updated_at")
            logging.info(updated_at)
            parsed_date = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            parsed_date = "{0}Z".format(
                parsed_date.replace(microsecond=0).isoformat(timespec="milliseconds")
            )
            logging.info(f"New parsed date: {parsed_date}")
            data = self.fetch(updated_at=parsed_date)
            logging.info(json.dumps(data, indent=4))
            objects = data.get("objects", [])
            categories = [o for o in objects if o.get("type") == "CATEGORY"]
            self.handle_categories_update(categories)
            self.process(data, update=True)
        except Exception as e:
            traceback.print_exc()
            logging.error("SQUARE INVENTORY: %s" % e)

    def webhook_update_variant_stock(self, body: dict):
        for inventory_count in body.get("inventory_counts", []):
            catalog_object_id = inventory_count.get("catalog_object_id")
            location_id = inventory_count.get("location_id")
            self.update_variant_stock(
                origin_id=catalog_object_id, location_id=location_id
            )

    @transaction.atomic
    def map_go_upc(self) -> None:
        variants = (
            Variant.objects.order_by("id")
            .filter(product__inventory__location__retailer=self._retailer)
            .exclude(variantimage__image_id__isnull=False)
            .all()
        )
        paginator = Paginator(variants, 10)
        for page_number in paginator.page_range:
            page = paginator.page(page_number)

            for variant in page.object_list:
                upc = None
                if variant.upc:
                    upc = variant.upc
                elif variant.sku:
                    upc = variant.sku

                if upc is None or variant.is_modified_by_admin:
                    continue

                go_upc_information = {}
                try:
                    go_upc_information = self._go_upc_client.get_product_information(
                        upc
                    )
                    if len(go_upc_information) == 0:
                        logging.info(f"No information found for {variant.pk}")
                        continue
                except Exception as e:
                    logging.error(f"Error fetching Go UPC Information with upc {upc}")
                    logging.error(e)

                go_upc_description = go_upc_information.get("description")

                if go_upc_description and go_upc_description != "No description found.":
                    variant.description = go_upc_description

                variant.save()

                try:
                    image_name, image = self._go_upc_client.get_product_image_from_url(
                        go_upc_information.get("imageUrl"), upc
                    )
                    if image is None:
                        logging.info(f"No image found for {variant.pk}")
                        continue

                    self.create_or_update_images(
                        variant=variant,
                        image=image,
                        image_id=f"{image_name}_{variant.id}",
                    )

                except Exception as e:
                    logging.error(f"Error fetching Go UPC Image with upc {upc}")
                    logging.error(e)
