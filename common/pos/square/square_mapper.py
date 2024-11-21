class Item:
    def __init__(self, data: dict):
        item_data: dict = data.get("item_data", {})
        variations: [] = item_data.get("variations", [])

        self.origin_id = data.get("id")
        self.locations = data.get("locations")
        self.name = item_data.get("name")
        self.is_deleted = data.get("is_deleted", False)
        self.variants = [ItemVariation(var) for var in variations]
        self.category_id = item_data.get("category_id")
        self.image_ids = item_data.get("image_ids", [])

        if len(self.variants) > 0:
            self.variants[0].image_ids += self.image_ids

    def __str__(self):
        return f"""
        Item:
            - origin_id: {self.origin_id}
            - locations: {self.locations}
            - name: {self.name}
            - is_deleted: {self.is_deleted}
            - variants: {self.variants}
            - category_id: {self.category_id}
        """

    def __repr__(self):
        return str(self)


class ItemVariation:
    def __init__(self, data: dict):
        variation_data = ItemVariationData(data["item_variation_data"])

        self.origin_id = data.get("id", None)
        self.origin_parent_id = variation_data.item_id
        self.name = variation_data.name
        self.sku = variation_data.sku
        self.upc = variation_data.upc
        self.stock = variation_data.stock
        self.price = variation_data.price
        self.description = ""
        self.currency = variation_data.currency
        self.locations = data.get("locations")
        self.is_deleted = data.get("is_deleted", False)
        self.location_overrides = variation_data.location_overrides
        self.image_ids = variation_data.image_ids

    def __str__(self):
        return f"""
        ItemVariation:
            - origin_id: {self.origin_id}
            - origin_parent_id: {self.origin_parent_id}
            - name: {self.name}
            - sku: {self.sku}
            - upc: {self.upc}
            - stock: {self.stock}
            - price: {self.price}
            - currency: {self.currency}
            - locations: {self.locations}
            - is_deleted: {self.is_deleted}
            - location_overrides: {self.location_overrides}
            - images: {self.image_ids}
        """

    def __repr__(self):
        return str(self)


class ItemVariationData:
    def __init__(self, data: dict):
        self.item_id = data["item_id"]
        self.name = data["name"]
        self.sku = data.get("sku", "")
        self.upc = data.get("upc", "")
        self.stock = data.get("stock", 0)
        self.price = self.get_price(data)
        self.currency = self.get_currency(data)
        self.location_overrides = data.get("location_overrides", [])
        self.image_ids = data.get("image_ids", [])

    def __str__(self):
        return f"""
        ItemVariationData:
            - item_id: {self.item_id}
            - name: {self.name}
            - sku: {self.sku}
            - upc: {self.upc}
            - stock: {self.stock}
            - price: {self.price}
            - currency: {self.currency}
            - location_overrides: {self.location_overrides}
        """

    def __repr__(self):
        return str(self)

    def get_price(self, data: dict):
        amount = data.get("price_money", {}).get("amount", 0)
        price = f"{(amount // 100)}.{(amount % 100):02}"
        return float(price)

    def get_currency(self, data: dict):
        return data.get("price_money", {}).get("currency", "USD")


class SquareInventoryMapper:
    def __init__(self, data: dict, locations: list[dict]):
        self.data = data
        self.locations = locations

    def exclude(self, values, exclude):
        return [id for id in values if id not in exclude]

    def filter(self, values, present):
        return [id for id in values if id in present]

    def set_location(self, locations, item: dict):
        in_all = item.get("present_at_all_locations", False)
        absent = item.get("absent_at_location_ids", [])
        in_locations = item.get("present_at_location_ids", [])

        if in_all and not in_locations and not absent:
            return list(locations)

        elif in_all and absent and not in_locations:
            return self.exclude(locations, absent)

        elif not in_all and in_locations and absent:
            return self.exclude(self.filter(locations, in_locations), absent)

        elif not in_all and in_locations and not absent:
            return in_locations
        else:
            return False

    def group_by_location(self, objects: list[dict]):
        result = []
        locations = set(location.pos_id for location in self.locations)

        for product in objects:
            product["locations"] = self.set_location(locations, product)

            if not product["locations"]:
                continue

            variations = product.get("item_data", {}).get("variations", [])

            for variant in variations:
                variant["locations"] = self.set_location(locations, variant)

                if not variant["locations"]:
                    continue

            result.append(product)

        return result

    def get_mapped_data(self):
        objects = self.data.get("objects", [])
        filtered_items = self.group_by_location(objects)
        items = [Item(obj) for obj in filtered_items if obj.get("type", "") == "ITEM"]
        return items
