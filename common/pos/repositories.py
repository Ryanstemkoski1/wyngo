from django.db.models import Min, Max, F, Sum

from inventories.models import Inventory as InventoryModel
from inventories.models import Product as ProductModel
from inventories.models import Variant as VariantModel
from inventories.models import VariantImage as VariantImageModel
from retailer.models import Location as LocationModel


class ProductRepository:
    def __init__(self) -> None:
        self.model = ProductModel

    def update_min_max_price(self, retailer_id, product_id):
        queryset = (
            self.model.objects.values(
                _min_price=Min("variants__price"), _max_price=Max("variants__price")
            )
            .filter(inventory__location__retailer_id=retailer_id, origin_id=product_id)
            .annotate(product_id=F("id"))
        )

        for product in queryset:
            self.model.objects.filter(id=product["product_id"]).update(
                min_price=product["_min_price"], max_price=product["_max_price"]
            )

    def get_by_origin_id(self, origin_id: str):
        return self.model.objects.filter(origin_id=origin_id)

    def update_or_create(self, product: ProductModel):
        exists = self.model.objects.filter(
            origin_id=product.origin_id, inventory=product.inventory
        ).exists()

        if not exists:
            product.save()
        else:
            self.get_by_origin_id(product.origin_id).update(
                name=product.name,
                min_price=product.min_price,
                max_price=product.max_price,
            )
        return product

    def check_product_exists(self, origin_id: str, location_id: str) -> ProductModel:
        return self.model.objects.get(
            origin_id=origin_id, inventory__location__pos_id=location_id
        )

    def update_total_stock(self, retailer_id: str):
        queryset = self.model.objects.filter(
            inventory__location__retailer_id=retailer_id,
        )

        for product in queryset:
            total_stock = product.variants.aggregate(Sum("stock")).get("stock__sum")

            if not total_stock:
                total_stock = 0

            self.model.objects.filter(id=product.id).update(total_stock=total_stock)

    def delete_products(self, deleted_products: list):
        for product in deleted_products:
            for location_id in product.locations:
                product = self.model.objects.filter(
                    origin_id=product.origin_id, inventory__location__pos_id=location_id
                ).first()
                if product is not None:
                    # TODO: Delete products and variants logically
                    product.delete()


class VariantRepository:
    def __init__(self) -> None:
        self.model = VariantModel

    def update_or_create(self, variant: VariantModel) -> None:
        exists = self.model.objects.filter(
            origin_id=variant.origin_id,
            product__inventory__id=variant.product.inventory.id,
        ).exists()

        if not exists:
            return variant.save()
        else:
            return self.model.objects.filter(origin_id=variant.origin_id).update(
                origin_id=variant.origin_id,
                origin_parent_id=variant.origin_parent_id,
                name=variant.name,
                sku=variant.sku,
                price=variant.price,
                currency=variant.currency,
                stock=variant.stock,
            )

    def get_by_retailer_id(self, retailer_id: str):
        return self.model.objects.values(
            "id",
            "origin_id",
            pos_id=F("product__inventory__location__pos_id"),
        ).filter(
            product__inventory__location__retailer__id=retailer_id,
        )

    def get_by_location_id(self, location_id, origin_id):
        return self.model.objects.filter(
            origin_id=origin_id,
            product__inventory__location__pos_id=location_id,
        ).first()

    def update_stock(
        self,
        stock: int = 0,
        variant_id: str = "",
        variant_origin_id: str = "",
        location_id: str = "",
    ):
        if variant_id:
            self.model.objects.filter(id=variant_id).update(stock=stock)
        elif variant_origin_id and location_id:
            self.model.objects.filter(
                origin_id=variant_origin_id,
                product__inventory__location__pos_id=location_id,
            ).update(stock=stock)

    def delete_missing_variants(self, product, variant_ids: list):
        variants_missing_pos = self.model.objects.filter(
            product__origin_id=product.origin_id,
            product__inventory__location__pos_id__in=product.locations,
        ).exclude(origin_id__in=variant_ids)
        variants_missing_pos.delete()


class VarianImageRepository:
    def __init__(self) -> None:
        self.model = VariantImageModel

    def update_or_create(self, data):
        exist = VariantImageModel.objects.filter(image_id=data["image_id"]).exists()
        if not exist:
            VariantImageModel.objects.update_or_create(
                image_id=data.get("image_id"), defaults=data
            )


class InventoryRepository:
    def __init__(self) -> None:
        self.model = InventoryModel

    def get_by_location(self, location: LocationModel):
        return self.model.objects.filter(location=location)

    def get_by_pos_id(self, pos_id: str):
        return self.model.objects.get(location__pos_id=pos_id)

    def create(self, retailer_name: str, location: LocationModel):
        name = f"{retailer_name}  #{'{:06d}'.format(location.id)}"
        return self.model.objects.create(name=name, location=location)
