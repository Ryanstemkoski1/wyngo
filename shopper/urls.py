from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    HomePageView,
    RetailerListView,
    RetailerDetailsView,
    ShoppingCenterListView,
    ShoppingCenterDetailsView,
    ProductDetailsPageView,
    MakeReservationView,
    ReservationDetailsView,
    UpdateReservationView,
    CancelReservationView,
    ReservationsListView,
    ProductListSearchView,
    toggler_wishlist, WishlistView
)

urlpatterns = [
    path(
        "",
        HomePageView.as_view(),
        name="index",
    ),
    path(
        "retailers/",
        RetailerListView.as_view(template_name="retailer_list.html"),
        name="retailers",
    ),
    path(
        "retailers/<int:retailer_id>/",
        RetailerDetailsView.as_view(template_name="retailer_details.html"),
        name="retailer-details",
    ),
    path(
        "shopping-centers/", ShoppingCenterListView.as_view(), name="shopping-centers"
    ),
    path(
        "shopping-centers/<int:shopping_center_id>/",
        ShoppingCenterDetailsView.as_view(template_name="shopping_center_details.html"),
        name="shopping-center-details",
    ),
    path(
        "products/<int:product_id>/",
        ProductDetailsPageView.as_view(),
        name="products",
    ),
    path(
        "make-reservation/<int:product_id>/",
        MakeReservationView.as_view(),
        name="make-reservation",
    ),
    path(
        "reservation/<int:reservation_id>/",
        ReservationDetailsView.as_view(),
        name="reservation-details",
    ),
    path(
        "update-reservation/<int:reservation_id>/",
        UpdateReservationView.as_view(),
        name="update-reservation",
    ),
    path(
        "cancel-reservation/<int:reservation_id>/",
        CancelReservationView.as_view(),
        name="cancel-reservation",
    ),
    path(
        "reservations/",
        ReservationsListView.as_view(),
        name="reservations",
    ),
    path(
        "products/",
        ProductListSearchView.as_view(),
        name="search-products",
    ),
    path(
        "wishlist/",
        WishlistView.as_view(),
        name="wishlist",
    ),
    path(
        "api/toggle-wishlist/",
        toggler_wishlist,
        name="toggle-wishlist",
    )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
