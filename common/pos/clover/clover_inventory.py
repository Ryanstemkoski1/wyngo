import json
import logging
import traceback

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction

from common.pos.clover.clover_client import CloverRequestClient
from common.pos.inventory import Inventory
from common.pos.utils import format_price, get_product_prices
from inventories.models import Variant, Product


class CloverInventory(Inventory):
    PLATFORM = "CLOVER"

    def __init__(self, retailer, offset=0, limit=10):
        super().__init__(retailer)
        self._request_client = CloverRequestClient(
            retailer.access_token, retailer.merchant_id
        )
        self._merchant_id = retailer.merchant_id
        self._mapper = CloverProductMapper(self._request_client)
        self._offset = offset
        self._limit = limit

    def fetch(self, item_id: str = None):
        return (
            self._request_client.get_inventory(limit=self._limit, offset=self._offset)
            if item_id is None
            else self._request_client.get_single_item(item_id)
        )

    def _fetch_recursive(self, offset=None, limit=None):
        if offset is None:
            offset = self._offset
        if limit is None:
            limit = self._limit

        items = []
        response = self._request_client.get_items(limit, offset)

        if "elements" in response:
            items.extend(response["elements"])

            if len(response["elements"]) < limit:
                return items
            else:
                offset += limit
                cache.set(f"{self._merchant_id}_offset", offset, None)
                items.extend(self._fetch_recursive(offset, limit))
        return items

    @transaction.atomic
    def store(self, products):
        for product in products:
            product_db: Product = Product.objects.filter(
                origin_id=product["origin_id"]
            ).first()
            if product_db is not None:
                if product_db.is_modified_by_admin:
                    product["name"] = product_db.name

            created_product = self.update_or_create_product(
                {
                    "origin": self.PLATFORM,
                    "origin_id": product["origin_id"],
                    "name": product["name"],
                    "min_price": product["min_price"],
                    "max_price": product["max_price"],
                    "inventory": self._inventory,
                    "total_stock": 0,
                }
            )

            for variant in product.get("variants"):
                variant_db: Variant = Variant.objects.filter(
                    origin_id=variant["origin_id"]
                ).first()
                if variant_db is not None:
                    if variant_db.is_modified_by_admin:
                        variant["name"] = variant_db.name
                        variant["description"] = variant_db.description

                new_variant = self.update_or_create_variant(
                    {
                        "origin_id": variant["origin_id"],
                        "origin_parent_id": variant["origin_parent_id"],
                        "name": variant["name"],
                        "sku": variant["sku"],
                        "upc": variant["upc"],
                        "stock": variant["stock"],
                        "price": variant["price"],
                        "currency": variant["currency"],
                        "product": created_product,
                    },
                    created_product,
                )

            variants = Variant.objects.filter(
                product__origin_id=created_product.origin_id
            )
            created_product.total_stock = sum(variant.stock for variant in variants)
            if len(variants) > 1:
                created_product.min_price = min(variant.price for variant in variants)
                created_product.max_price = max(variant.price for variant in variants)
            created_product.save()

    def process(self, products):
        mapped_data = self._mapper.map(products)
        # self.run_go_upc(mapped_data)
        self.store(mapped_data)

    def map_go_upc_information(
        self, go_upc_information: dict, variant: dict, code: str
    ):
        if len(go_upc_information) != 0:
            variant["description"] = go_upc_information.get(
                "description", variant.get("description")
            )
            variant["images"] = [
                self._go_upc_client.get_product_image_from_url(
                    go_upc_information.get("imageUrl"), code
                )
            ]

    def run(self, item_id: str = None, offset: int = 0, limit: int = 0):
        try:
            self._inventory = self.get_or_create_inventories()

            products = self.fetch(item_id=item_id)
            if not products.get("elements", []):
                return {
                    "result": True,
                    "fetch_next": False,
                }

            self.process(products)
            return (
                {
                    "result": True,
                    "fetch_next": True,
                    "retailer_id": self._retailer.pk,
                    "limit": self._limit,
                    "offset": self._offset + self._limit,
                }
                if item_id is None
                else {
                    "result": True,
                    "fetch_next": False,
                }
            )

        except Exception as e:
            traceback.print_exc()
            id = self._retailer.id
            logging.error(
                f"ERROR LOADING CLOVER INVENTORY for Retailer id {id}: {str(e)}"
            )
            return {
                "result": False,
                "fetch_next": False,
            }

    @transaction.atomic
    def map_go_upc(self) -> None:
        variants = (
            Variant.objects.order_by("created_at")
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

                    self.update_or_create_variant_image(
                        {
                            "variant": variant,
                            "image": image,
                            "image_id": f"{image_name}_{variant.id}",
                        }
                    )
                except Exception as e:
                    logging.error(f"Error fetching Go UPC Image with upc {upc}")
                    logging.error(e)

    @transaction.atomic
    def delete(self, item_id: str):
        self._inventory = self.get_or_create_inventories()
        self.delete_product(origin_id=item_id, inventory=self._inventory)

    @transaction.atomic
    def create_pos_item(self, product: Product):
        variants = product.variants.all()
        path = f"{self._merchant_id}/items"
        if len(variants) > 0:
            # first create the group
            group_path = f"{self._merchant_id}/item_groups"
            group = self._request_client._request(
                path=group_path,
                method="POST",
                json={
                    "name": product.name
                }
            )
            product.origin_id = group.get("id")
            product.save()

            # create attributes
            attributes_path = f"{self._merchant_id}/attributes"
            attributes_payload = {
                "itemGroup": {"id": group.get("id")},
                "name": f"variants-for-{product.name}",
            }
            attribute = self._request_client._request(
                path=attributes_path,
                method="POST",
                json=attributes_payload
            )
            attribute_id = attribute.get("id")

            for variant in variants:
                option_path = f"{self._merchant_id}/attributes/{attribute_id}/options"
                option = self._request_client._request(
                    path=option_path,
                    method="POST",
                    json={
                        "name": variant.name
                    }
                )
                # create item
                payload = {
                    "hidden": "false",
                    "available": "true",
                    "name": variant.name,
                    "price": int(variant.price) * 100,
                    "stockCount": variant.stock,
                    "sku": variant.sku,
                    "code": variant.upc,
                    "itemGroup": {
                        "id": group.get("id")
                    },
                    "options": [
                        {
                            "attribute": {"id": attribute_id},
                            "name": variant.name,
                            "id": option.get("id"),
                        }
                    ]
                }
                response = self._request_client._request(
                    path=path,
                    method="POST",
                    json=payload
                )

                # Link item to variant
                self._request_client._request(
                    path=f"{self._merchant_id}/option_items",
                    method="POST",
                    json={
                        "elements":
                        [
                            {
                                "option":
                                {
                                    "id": option.get("id")
                                },
                                "item":
                                {
                                    "id": response.get("id")
                                }
                            },
                        ]
                    }
                )
                variant.origin_id = response.get("id")
                variant.origin_parent_id = group.get("id")
                variant.name = response.get("name") + " " + variant.name
                variant.save()

        else:
            payload = {
                "hidden": "false",
                "available": "true",
                "name": product.name,
                "price": int(product.min_price) * 100,
                "stockCount": product.total_stock,
            }
            item = self._request_client._request(
                path=path,
                method="POST",
                json=payload
            )
            product.origin_id = item.get("id")
            product.save()

    def update_pos_item(self, product: Product, form, formset):
        # First PUT group_items
        if form.changed_data and 'name' in form.changed_data:
            payload = {
                "name": product.name,
            }
            path = f"{self._merchant_id}/item_groups/{product.origin_id}"
            self._request_client._request(
                path=path,
                method="POST",
                json=payload
            )

        if len(formset.deleted_objects) > 0:
            item_ids = ','.join([x.origin_id for x in formset.deleted_objects if x.origin_id])
            if item_ids:
                path = f"{self._merchant_id}/items/?itemIds={item_ids}"
                self._request_client._request(
                    path=path,
                    method="DELETE"
                )

        if len(formset.new_objects) > 0:
            group_id = product.origin_id
            attributes = self._request_client._request(
                path=f"{self._merchant_id}/attributes",
                method="GET",
                params={
                    "itemGroup.id": group_id
                }
            )
            attribute_id = attributes.get("elements")[0].get("id") if attributes.get("elements") else None
            if attribute_id is None:
                return
            for variant in formset.new_objects:
                # create option
                option_path = f"{self._merchant_id}/attributes/{attribute_id}/options"
                option = self._request_client._request(
                    path=option_path,
                    method="POST",
                    json={
                        "name": variant.name
                    }
                )
                # create item
                payload = {
                    "hidden": "false",
                    "available": "true",
                    "name": variant.name,
                    "price": int(variant.price) * 100,
                    "stockCount": variant.stock,
                    "sku": variant.sku,
                    "code": variant.upc,
                    "itemGroup": {
                        "id": group_id
                    },
                    "options": [
                        {
                            "attribute": {"id": attribute_id},
                            "name": variant.name,
                            "id": option.get("id"),
                        }
                    ]
                }
                response = self._request_client._request(
                    path=f"{self._merchant_id}/items",
                    method="POST",
                    json=payload
                )

                # Link item to variant
                self._request_client._request(
                    path=f"{self._merchant_id}/option_items",
                    method="POST",
                    json={
                        "elements":
                            [
                                {
                                    "option":
                                        {
                                            "id": option.get("id")
                                        },
                                    "item":
                                        {
                                            "id": response.get("id")
                                        }
                                },
                            ]
                    }
                )

                variant.origin_id = response.get("id")
                variant.origin_parent_id = group_id
                variant.name = response.get("name") + " " + variant.name
                variant.save()

        if len(formset.changed_objects) > 0:
            for obj in formset.changed_objects:
                variant = obj[0]
                payload = {
                    "hidden": "false",
                    "available": "true",
                    # "name": variant.name, // name is not updatable
                    "price": int(variant.price) * 100,
                    "stockCount": variant.stock,
                    "sku": variant.sku,
                    "code": variant.upc,
                    "itemGroup": {
                        "id": product.origin_id
                    },
                }
                path = f"{self._merchant_id}/items/{variant.origin_id}"
                self._request_client._request(
                    path=path,
                    method="POST",
                    json=payload
                )

    def delete_pos_product(self, product):
        if not product.origin_id:
            return
        path = f"{self._merchant_id}/item_groups/{product.origin_id}"
        self._request_client._request(
            path=path,
            method="DELETE"
        )

        variants = product.variants.all()
        variants_ids = ','.join([x.origin_id for x in variants if x.origin_id])
        if variants_ids:
            path = f"{self._merchant_id}/items/?itemIds={variants_ids}"
            self._request_client._request(
                path=path,
                method="DELETE"
            )


class CloverProductMapper:
    def __init__(self, clover_client):
        self._clover_client = clover_client

    def get_item_group(self, group_id):
        return self._clover_client.get_item_group(group_id)

    def map(self, products):
        result_product = []
        if not products:
            return False

        mapped_groups = self.map_groups(products)

        for item in mapped_groups:
            result_product.append(self.map_products(item))

        return result_product

    def map_groups(self, products):
        result = []
        grouped_items = {}

        for item in products["elements"]:
            if "itemGroup" in item:
                group_id = item["itemGroup"]["id"]

                if group_id not in grouped_items:
                    itemGroup = self.get_item_group(group_id)
                    group = {
                        "id": itemGroup["id"],
                        "name": itemGroup["name"],
                        "variations": [],
                    }
                    grouped_items[group_id] = group
                    result.append(group)

                grouped_items[group_id]["variations"].append(item)

            else:
                result.append(
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "variations": [
                            {
                                "itemGroup": {
                                    "id": item["id"],
                                },
                                **item,
                            }
                        ],
                    }
                )

        return result

    def map_products(self, item):
        variations = item.get("variations", [])
        variants = self.map_variants(variations)
        prices = get_product_prices(variants)

        product = {
            "origin_id": item.get("id", ""),
            "name": item.get("name", ""),
            "description": "",  # TODO: create method to get description if it exists
            "images": [],  # TODO: create method to retrieve image urls
            "variants": variants,
            "total_stock": 0,
            **prices,
        }
        return product

    def map_variants(self, variations):
        _variants = []
        for variant in variations:
            price, currency = (
                variant.get("price", 0),
                "USD",  # TODO: get currency from clover
            )
            stock = variant.get("itemStock", {}).get("stockCount", 0)

            _variants.append(
                {
                    "origin_id": variant.get("id", ""),
                    "origin_parent_id": variant.get("itemGroup", {}).get("id"),
                    "name": variant.get("name", ""),
                    "sku": variant.get("sku", ""),
                    "upc": variant.get("code", ""),
                    "description": variant.get("description", ""),
                    "stock": stock,
                    "price": format_price(price),
                    "currency": currency,
                    "images": [],  # TODO: create method to retrieve image urls
                }
            )

        return _variants
