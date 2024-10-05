from django.db import models

from common.models import BaseTimeModel


class ProductWishlist(BaseTimeModel):
    product = models.ForeignKey(
        "inventories.Product", on_delete=models.CASCADE, related_name="wishlist"
    )
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="product_wishlist")

    class Meta:
        unique_together = ("user", "product")


class RetailerWishlist(BaseTimeModel):
    retailer = models.ForeignKey(
        "retailer.Retailer", on_delete=models.CASCADE, related_name="wishlist"
    )
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="retailer_wishlist")

    class Meta:
        unique_together = ("user", "retailer")
