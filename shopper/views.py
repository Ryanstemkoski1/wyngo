import datetime
import json
import random
import uuid

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import (
    F,
    Min,
    Subquery,
    OuterRef,
    DecimalField,
)
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, UpdateView
from faker import Faker

from common.pos.clover.clover_reservation import CloverReservation
from common.pos.square.square_reservation import SquareReservation
from inventories.models import Product, Variant, Reservation
from retailer.models import Category, Retailer
from shopper.models import ProductWishlist, RetailerWishlist

# Create your views here.

fake = Faker()


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        template_name = "index.html"

        near_you = []
        just_added = []
        upcoming_reservations = []
        product_id = 0

        lowest_variant_price_upc_subquery = (
            Variant.objects.filter(upc=OuterRef("variants__upc"), price__gt=0.00)
            .values("upc")
            .annotate(lowest_variant_price=Min("price"))
            .values("lowest_variant_price")[:1]
        )
        lowest_variant_price_sku_subquery = (
            Variant.objects.filter(sku=OuterRef("variants__sku"), price__gt=0.00)
            .values("sku")
            .annotate(lowest_variant_price=Min("price"))
            .values("lowest_variant_price")[:1]
        )

        products_with_ordered_variants_upc = (
            Product.objects.annotate(
                variant_count=Count("variants"),
                lowest_variant_price_upc=Subquery(
                    lowest_variant_price_upc_subquery, output_field=DecimalField()
                ),
            )
            .filter(
                Q(variants__price=F("lowest_variant_price_upc"))
                | Q(variants__upc="") & Q(variants__price__gt=0.00),
                variant_count=1,
            )
            .order_by("lowest_variant_price_upc")
        )
        products_with_ordered_variants_sku = (
            Product.objects.annotate(
                variant_count=Count("variants"),
                lowest_variant_price_sku=Subquery(
                    lowest_variant_price_sku_subquery, output_field=DecimalField()
                ),
            )
            .filter(
                Q(variants__price=F("lowest_variant_price_sku"))
                | Q(variants__sku="") & Q(variants__price__gt=0.00),
                variant_count=1,
            )
            .order_by("lowest_variant_price_sku")
        )

        products_with_empty_upc_variants = Product.objects.filter(
            Q(variants__price__gt=0.00) & (Q(variants__upc="")
            | Q(
                variants__upc__isnull=True,
            ))
        ).annotate(variant_count=Count("variants"))

        products_with_empty_sku_variants = Product.objects.filter(
            Q(variants__price__gt=0.00) & (Q(variants__sku="")
            | Q(
                variants__sku__isnull=True,
            ))
        ).annotate(variant_count=Count("variants"))

        products = (
            products_with_ordered_variants_upc
            | products_with_ordered_variants_sku
            | products_with_empty_upc_variants
            | products_with_empty_sku_variants
        )

        if request.user.is_authenticated:
            upcoming_reservations = Reservation.objects.filter(
                user=request.user,
                time_limit__gte=datetime.datetime.now(),
                status="RESERVED",
            ).order_by("-time_limit")
        else:
            upcoming_reservations = []

        upc_set = set()
        for product in products.order_by("variants__price"):
            if product_id != product.id and product.is_active:
                can_continue = True
                for variant in product.variants.all():
                    if variant.upc in upc_set or variant.sku in upc_set:
                        can_continue = False
                        break
                    else:
                        can_continue = True
            
                    if variant.upc:
                        upc_set.add(variant.upc)
                    if variant.sku:
                        upc_set.add(variant.sku)
                if can_continue:
                    near_you.append(product)
                    just_added.append(product)
                    product_id = product.id

        for res in upcoming_reservations:
            for product in near_you:
                if res.variant.product.id == product.id:
                    near_you.remove(product)

            for product in just_added:
                if res.variant.product.id == product.id:
                    just_added.remove(product)

        retailers_query = Retailer.objects.filter(status=Retailer.STATUS_APPROVED)
        retailers = []

        for retailer in retailers_query:
            variants = Variant.objects.filter(
                product__inventory__location__retailer=retailer,
                price__gt=0.00,
            ).count()

            if variants > 0:
                retailers.append(retailer)

        near_you = random.sample(near_you, len(near_you))[:16]
        just_added = random.sample(just_added, len(just_added))[:16]

        user_product_wishlist = {}
        if request.user.is_authenticated:
            wishlist = ProductWishlist.objects.filter(user=request.user, product__in=products).all()
            for wish in wishlist:
                user_product_wishlist[wish.product.id] = True

        user_retailers_wishlist = {}
        if self.request.user.is_authenticated:
            wishlist = RetailerWishlist.objects.filter(user=self.request.user).all()
            for wish in wishlist:
                user_retailers_wishlist[wish.retailer.id] = True

        return render(
            request,
            template_name,
            {
                "near_you": near_you,
                "just_added": just_added,
                "retailers": retailers,
                "upcoming_reservations": upcoming_reservations,
                "user_products_wishlist": user_product_wishlist,
                "user_retailers_wishlist": user_retailers_wishlist,
            },
        )


class RetailerListView(ListView):
    model = Retailer
    context_object_name = "retailers"
    paginate_by = 80

    def get_queryset(self):
        category_name = self.request.GET.get("category")

        qfilter = Q(
            id__isnull=False,
            status=Retailer.STATUS_APPROVED
        )

        if category_name and category_name not in ["all", ""]:
            qfilter.add(Q(category__name__icontains=category_name), qfilter.connector)

        retailes_query = Retailer.objects.filter(qfilter)

        queryset = []

        for retailer in retailes_query:
            variants = Variant.objects.filter(
                product__inventory__location__retailer=retailer,
                price__gt=0.00,
            ).count()

            if variants > 0:
                queryset.append(retailer)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = self.get_queryset()

        paginator = Paginator(queryset, self.paginate_by)

        page_number = self.request.GET.get("page")

        page_obj = paginator.get_page(page_number)

        context["page_obj"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()
        context["categories"] = (
            Category.objects.values("name", "id")
            .annotate(retailer_count=Count("retailer"))
            .order_by("name")
        )
        context["score"] = random.randint(1, 100)
        context["current_category"] = self.request.GET.get("category")

        user_retailers_wishlist = {}
        if self.request.user.is_authenticated:
            wishlist = RetailerWishlist.objects.filter(user=self.request.user).all()
            for wish in wishlist:
                user_retailers_wishlist[wish.retailer.id] = True
        context["user_retailers_wishlist"] = user_retailers_wishlist

        return context


class RetailerDetailsView(ListView):
    model = Retailer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        retailer_id = self.kwargs.get("retailer_id")

        qfilter = Q(
            id__isnull=False,
        )

        if retailer_id:
            qfilter.add(Q(id=retailer_id), qfilter.connector)

        retailer = Retailer.objects.filter(qfilter).last()

        products = list(
            Product.objects.filter(
                inventory__location__retailer=retailer,
                is_active=True,
            ).order_by("name")
        )

        upcoming_reservations = []

        if self.request.user.is_authenticated:
            upcoming_reservations = Reservation.objects.filter(
                user=self.request.user,
                time_limit__gte=datetime.datetime.now(),
                status="RESERVED",
            ).order_by("-time_limit")

            if len(upcoming_reservations) > 0:
                for res in upcoming_reservations:
                    for product in products:
                        if res.variant.product.id == product.id:
                            products.remove(product)

        paginator = Paginator(products, 80)

        page_number = self.request.GET.get("page")

        page_obj = paginator.get_page(page_number)
        previous_url = self.request.META.get("HTTP_REFERER", None)

        context["page_obj"] = page_obj
        context["score"] = random.randint(1, 100)
        context["retailer"] = retailer
        context["previous_url"] = previous_url
        context["home_url"] = self.request.build_absolute_uri(reverse("index"))
        origin = self.request.GET.get("origin", previous_url)
        context["origin"] = origin

        in_wishlist = self.request.user.is_authenticated and RetailerWishlist.objects.filter(
            user=self.request.user,
            retailer=retailer
        ).exists()
        context["in_wishlist"] = in_wishlist

        user_product_wishlist = {}
        if self.request.user.is_authenticated:
            wishlist = ProductWishlist.objects.filter(user=self.request.user, product__in=products).all()
            for wish in wishlist:
                user_product_wishlist[wish.product.id] = True

        context["user_products_wishlist"] = user_product_wishlist
        return context


class ShoppingCenterListView(TemplateView):
    template_name = "shopping_center_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shopping_centers = []

        names = [
            "The Mall of Wonders",
            "The Oasis Shopping Center",
            "The Promenade",
            "The Shops at the Creek",
            "The Village at the Mall",
        ]

        for i in range(5):
            shopping_centers.append(
                {
                    "id": i + 1,
                    "name": names[i],
                    "image": f"{names[i].replace(' ', '_').lower()}.jpg",
                    "location": fake.address(),
                }
            )

        shopping_centers = shopping_centers * 4

        random.shuffle(shopping_centers)

        paginator = Paginator(shopping_centers, 8)

        page_number = self.request.GET.get("page")

        page_obj = paginator.get_page(page_number)

        context["shopping_centers"] = page_obj

        return context


class ShoppingCenterDetailsView(TemplateView):
    template_name = "shopping_center_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shopping_center_id = self.kwargs.get("shopping_center_id")

        data = {
            1: {
                "id": 1,
                "name": "The Mall of Wonders",
                "image": "the_mall_of_wonders.jpg",
                "cover": "https://picsum.photos/id/299/800",
                "location": fake.address(),
                "description": fake.paragraph(nb_sentences=10),
            },
            2: {
                "id": 2,
                "name": "The Oasis Shopping Center",
                "image": "the_oasis_shopping_center.jpg",
                "cover": "https://picsum.photos/id/299/800",
                "location": fake.address(),
                "description": fake.paragraph(nb_sentences=10),
            },
            3: {
                "id": 3,
                "name": "The Promenade",
                "image": "the_promenade.jpg",
                "cover": "https://picsum.photos/id/299/800",
                "location": fake.address(),
                "description": fake.paragraph(nb_sentences=10),
            },
            4: {
                "id": 4,
                "name": "The Shops at the Creek",
                "image": "the_shops_at_the_creek.jpg",
                "cover": "https://picsum.photos/id/299/800",
                "location": fake.address(),
                "description": fake.paragraph(nb_sentences=10),
            },
            5: {
                "id": 5,
                "name": "The Village at the Mall",
                "image": "the_village_at_the_mall.jpg",
                "cover": "https://picsum.photos/id/299/800",
                "location": fake.address(),
                "description": fake.paragraph(nb_sentences=10),
            },
        }

        shopping_center = data.get(shopping_center_id)
        products = []
        retailers = []

        retailer_names = [
            "Flavors of The Earth",
            "Gourmet Bakery",
            "The Bakery on The Corner",
            "The Bread of Quality",
            "The Mom_s Oven",
            "The Sweet Spot",
        ]

        product_names = [
            "Cheesecake 40oz",
            "Freshness Guaranteed Croissant",
            "Freshness Guaranteed Strawberry",
            "Halloween Sugar Cookies",
            "Marketside Blueberry Muffins 2",
            "Marketside Blueberry Muffins",
            "Pumpkin Bread",
            "Sliced Brioche Bread",
        ]

        for i in range(8):
            score = fake.pydecimal(left_digits=2, right_digits=2, positive=True)
            products.append(
                {
                    "id": f"{i + 1}",
                    "name": product_names[i],
                    "min_price": fake.pydecimal(
                        left_digits=2, right_digits=2, positive=True
                    ),
                    "max_price": fake.pydecimal(
                        left_digits=2, right_digits=2, positive=True
                    ),
                    "image": {
                        "url": f"{product_names[i].replace(' ', '_').lower()}.jpg",
                    },
                    "score": score,
                    "score_color": "success"
                    if score > 50
                    else "warning"
                    if score > 30
                    else "danger"
                    if score > 10
                    else "N/A",
                    "retailer_name": random.choice(retailer_names),
                    "address": fake.address(),
                    "quantity": fake.pyint(min_value=1, max_value=100),
                    "offers": fake.pyint(min_value=1, max_value=20),
                }
            )

        for i in range(6):
            score = fake.pydecimal(left_digits=2, right_digits=2, positive=True)
            retailers.append(
                {
                    "id": i + 1,
                    "name": retailer_names[i],
                    "image": f"{retailer_names[i].replace(' ', '_').lower()}.jpg",
                    "score": score,
                    "score_color": "success"
                    if score > 50
                    else "warning"
                    if score > 30
                    else "danger"
                    if score > 10
                    else "N/A",
                    "address": fake.address(),
                }
            )

        context["products"] = products
        context["retailers"] = retailers
        context["sc"] = shopping_center

        return context


class ProductDetailsPageView(TemplateView):
    def get(self, request, **kwargs):
        template_name = "product_details.html"

        product_id = self.kwargs.get("product_id")

        other_retailers = []

        related_items = []

        product = (
            Product.objects.filter(
                id=product_id,
            )
            .order_by("variants__price")
            .last()
        )

        lowest_variant_price_subquery = (
            Variant.objects.filter(upc=OuterRef("variants__upc"))
            .values("upc")
            .annotate(lowest_variant_price=Min("price"))
            .values("lowest_variant_price")[:1]
        )

        products_with_ordered_variants = (
            Product.objects.annotate(
                variant_count=Count("variants"),
                lowest_variant_price=Subquery(
                    lowest_variant_price_subquery, output_field=DecimalField()
                ),
            )
            .filter(
                Q(variants__price=F("lowest_variant_price"))
                | Q(variants__upc__isnull=True)
                | Q(variants__upc=""),
                variant_count=1,
            )
            .order_by("lowest_variant_price")
            .exclude(id=product.id)
        )

        products_with_empty_upc_variants = (
            Product.objects.filter(
                Q(variants__upc__isnull=True) | Q(variants__upc=""),
            )
            .annotate(variant_count=Count("variants"))
            .exclude(id=product.id)
        )

        products = products_with_ordered_variants | products_with_empty_upc_variants

        p_id = 0

        for product_related in products.order_by("id"):
            if p_id != product_related.id and product_related.is_active:
                related_items.append(product_related)

            p_id = product_related.id

        if request.user.is_authenticated and not request.user.is_staff:
            upcoming_reservations = Reservation.objects.filter(
                user=request.user,
                time_limit__gte=datetime.datetime.now(),
                status="RESERVED",
            ).order_by("-time_limit")
        else:
            upcoming_reservations = []

        for res in upcoming_reservations:
            for item in related_items:
                if res.variant.product.id == item.id:
                    related_items.remove(item)

        product_variants = Variant.objects.filter(
            product=product, price__gt=0
        ).order_by("price")

        variant_images = [
            {
                "id": variant.id,
                "images": [image.image.url for image in variant.variantimage_set.all()],
            }
            for variant in product_variants
        ]
        if product.variants.first().upc and not product.variants.first().sku:
            upc = product.variants.first().upc
        elif product.variants.first().sku and not product.variants.first().upc:
            upc = product.variants.first().sku
        elif product.variants.first().sku and product.variants.first().upc:
            upc = product.variants.first().upc
        else:
            upc = None

        if upc:
            other_retailers = (
                Product.objects.filter(
                    Q(variants__upc=upc) | Q(variants__sku=upc),
                    is_active=True,
                    variants__price__gt=0,
                )
                .exclude(
                    inventory__location__retailer=product.inventory.location.retailer
                )
                .order_by("variants__price", "-total_stock")[:8]
            )

        previous_url = request.META.get("HTTP_REFERER", None)

        origin = reverse("index")

        if previous_url and "retailers" in previous_url:
            origin = reverse("retailers")

        user_products_wishlist = {}
        if self.request.user.is_authenticated:
            wishlist = ProductWishlist.objects.filter(user=self.request.user).all()
            for wish in wishlist:
                user_products_wishlist[wish.product.id] = True

        return render(
            request,
            template_name,
            {
                "related_items": related_items,
                "product": product,
                "product_variants": product_variants,
                "other_retailers": other_retailers,
                "variants_json": json.dumps(variant_images),
                "previous_url": previous_url,
                "origin": origin,
                "user_products_wishlist": user_products_wishlist,
            },
        )


class MakeReservationView(TemplateView):
    def post(self, request, **kwargs):
        previous_url = request.META.get("HTTP_REFERER", "")
        if request.user.is_anonymous:
            return redirect("login")

        if request.user.is_staff:
            url = reverse("logout") + f"?url=reservations"
            return redirect(url)

        product_id = self.kwargs.get("product_id")
        quantity = int(request.POST.get("quantity"))
        variation_id = request.POST.get("variation")

        if variation_id:
            variation = Variant.objects.filter(id=variation_id).last()
            merchant_id = variation.product.inventory.location.retailer.merchant_id
        else:
            variation = Product.objects.get(id=product_id).variants.first()
            merchant_id = variation.product.inventory.location.retailer.merchant_id

        retailer = (
            Retailer.objects.exclude(access_token__isnull=True)
            .exclude(merchant_id__exact="")
            .filter(merchant_id=merchant_id)
            .first()
        )

        total = int(variation.price) * quantity

        reservation = Reservation(
            user=request.user,
            variant=variation,
            origin=variation.product.origin,
            total=total,
            quantity=quantity,
            status="RESERVED",
            time_limit=datetime.datetime.now() + datetime.timedelta(minutes=45),
        )
        reservation.save()
        reservation.reservation_code = "#{:06d}".format(reservation.id)
        reservation.save()

        messages.success(
            request,
            "Successful reservation, you have 45 min to go for your product.",
            extra_tags="success",
        )

        return (
            redirect("reservation-details", reservation_id=reservation.id)
        )


        # if quantity > 2 and total > 50:
        #     messages.error(
        #         request,
        #         "We're sorry, but reservations for this product are currently limited to $50 total and 2 items per order. Please modify your reservation to stay within these limits.",
        #         extra_tags="error",
        #     )
        #
        #     return redirect(previous_url)

        line_items = []

        # if variation.product.origin == "CLOVER":
        #     for i in range(int(quantity)):
        #         line_items.append({"item": {"id": variation.origin_id}})
        #
        #     order_data = {
        #         "orderCart": {
        #             "lineItems": line_items,
        #             "note": "Order created on Wyndo App",
        #             "title": "Wyndo Order",
        #         }
        #     }
        #
        #     reservation_data = {
        #         "product": variation.id,
        #         "user": request.user.id,
        #         "quantity": quantity,
        #         "status": "RESERVED",
        #     }
        #
        #     data = {
        #         "order_params": order_data,
        #         "reservation_params": reservation_data,
        #     }
        #
        #     try:
        #         clover_reservation = CloverReservation(retailer)
        #         reservation = clover_reservation.run(data, "create")
        #
        #         if reservation is None:
        #             messages.error(
        #                 request,
        #                 "We're currently unable to process your reservation. Please try again later",
        #                 extra_tags="error",
        #             )
        #             return redirect(previous_url)
        #
        #         messages.success(
        #             request,
        #             "Successful reservation, you have 45 min to go for your product.",
        #             extra_tags="success",
        #         )
        #
        #         return (
        #             redirect("reservation-details", reservation_id=reservation.id)
        #             if "product" in previous_url.lower()
        #             else redirect(previous_url)
        #         )
        #
        #     except Exception as e:
        #         print(e)
        #
        # else:
        #     line_items.append(
        #         {
        #             "quantity": str(quantity),
        #             "catalog_object_id": variation.origin_id,
        #         }
        #     )
        #
        #     order_data = {
        #         "location_id": variation.product.inventory.location.pos_id,
        #         "line_items": line_items,
        #     }
        #
        #     reservation_data = {
        #         "product": variation.id,
        #         "user": request.user.id,
        #         "quantity": quantity,
        #         "status": "RESERVED",
        #     }
        #
        #     data = {
        #         "order_params": {
        #             "order": order_data,
        #             "idempotency_key": str(uuid.uuid4()),
        #         },
        #         "reservation_params": reservation_data,
        #     }
        #
        #     try:
        #         retailer = variation.product.inventory.location.retailer
        #         square_reservation = SquareReservation(retailer)
        #         reservation = square_reservation.run(data, "create")
        #
        #         if reservation is None:
        #             messages.error(
        #                 request,
        #                 "We're currently unable to process your reservation. Please try again later",
        #                 extra_tags="error",
        #             )
        #             return redirect(previous_url)
        #
        #         messages.success(
        #             request,
        #             "Successful reservation, you have 45 min to go for your product.",
        #             extra_tags="success",
        #         )
        #
        #         return (
        #             redirect("reservation-details", reservation_id=reservation.id)
        #             if "product" in previous_url.lower()
        #             else redirect(previous_url)
        #         )
        #
        #     except Exception as e:
        #         print(e)


class ReservationDetailsView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_anonymous:
            return redirect("login")

        template_name = "reservation_details.html"

        reservation_id = self.kwargs.get("reservation_id")

        reservation = Reservation.objects.filter(
            id=reservation_id, user=request.user
        ).last()

        product_variants = Variant.objects.filter(
            product=reservation.variant.product,
        ).order_by("price")

        variant_images = [
            {
                "id": variant.id,
                "images": [image.image.url for image in variant.variantimage_set.all()],
            }
            for variant in product_variants
        ]

        related_items = list(
            Product.objects.filter(
                inventory__location__retailer=reservation.variant.product.inventory.location.retailer,
                is_active=True,
            ).exclude(id=reservation.variant.product.id)
        )

        if request.user.is_authenticated:
            upcoming_reservations = Reservation.objects.filter(
                user=request.user,
                time_limit__gte=datetime.datetime.now(),
                status="RESERVED",
            ).order_by("-time_limit")
        else:
            upcoming_reservations = []

        for res in upcoming_reservations:
            for product in related_items:
                if res.variant.product.id == product.id:
                    related_items.remove(product)
        return render(
            request,
            template_name,
            {
                "reservation": reservation,
                "variants_json": json.dumps(variant_images),
                "product_variants": product_variants,
                "related_items": related_items,
            },
        )


class UpdateReservationView(TemplateView):
    def post(self, request, **kwargs):
        if request.user.is_anonymous:
            return redirect("login")

        previous_url = request.META.get("HTTP_REFERER", "")

        quantity = int(request.POST.get("quantity"))

        variant_id = request.POST.get("variation")

        reservation_id = self.kwargs.get("reservation_id")

        reservation = Reservation.objects.filter(id=reservation_id).last()

        if variant_id:
            variant = Variant.objects.filter(id=variant_id).last()
        else:
            variant = reservation.variant

        retailer = (
            Retailer.objects.exclude(access_token__isnull=True)
            .exclude(merchant_id__exact="")
            .filter(
                merchant_id=reservation.variant.product.inventory.location.retailer.merchant_id
            )
            .first()
        )

        total = quantity * variant.price

        reservation.quantity = quantity
        reservation.total = total
        reservation.save()

        messages.success(
            request,
            "Reservation updated successfully.",
            extra_tags="success",
        )

        return redirect(previous_url)

        # if reservation.variant.product.origin == "CLOVER":
        #     line_items = []
        #
        #     for i in range(int(quantity)):
        #         line_items.append({"item": {"id": variant.origin_id}})
        #
        #     data = {
        #         "line_item_params": line_items,
        #         "order_params": {
        #             "order_id": reservation.origin_id,
        #             "total": float(variant.price) * int(quantity) * 100,
        #             "note": "Order updated on Wyndo App",
        #             "title": "Wyndo Order",
        #         },
        #         "reservation_params": {
        #             "quantity": quantity,
        #             "product": variant.id,
        #         },
        #     }
        #
        #     try:
        #         clover_reservation = CloverReservation(retailer)
        #         clover_reservation.run(data, "update")
        #
        #         messages.success(
        #             request,
        #             "Reservation updated successfully.",
        #             extra_tags="success",
        #         )
        #
        #         return redirect(previous_url)
        #     except Exception as e:
        #         print(e)
        #
        # else:
        #     data = {
        #         "order_params": {
        #             "order": {
        #                 "location_id": variant.product.inventory.location.pos_id,
        #                 "line_items": [
        #                     {
        #                         "quantity": str(quantity),
        #                         "catalog_object_id": variant.origin_id,
        #                     }
        #                 ],
        #                 "version": reservation.version,
        #             },
        #             "idempotency_key": str(uuid.uuid4()),
        #             "fields_to_clear": ["line_items"],
        #         },
        #         "reservation_params": {
        #             "order_id": reservation.origin_id,
        #             "quantity": quantity,
        #             "product": variant.id,
        #         },
        #     }
        #
        #     try:
        #         retailer = variant.product.inventory.location.retailer
        #         square_reservation = SquareReservation(retailer)
        #         square_reservation.run(data, "update")
        #
        #         messages.success(
        #             request,
        #             "Reservation updated successfully.",
        #             extra_tags="success",
        #         )
        #
        #         return redirect(previous_url)
        #     except Exception as e:
        #         print(e)


class CancelReservationView(TemplateView):
    def post(self, request, **kwargs):
        if request.user.is_anonymous:
            return redirect("login")

        reservation_id = self.kwargs.get("reservation_id")

        reservation = Reservation.objects.filter(id=reservation_id).last()

        retailer = (
            Retailer.objects.exclude(access_token__isnull=True)
            .exclude(merchant_id__exact="")
            .filter(
                merchant_id=reservation.variant.product.inventory.location.retailer.merchant_id
            )
            .first()
        )

        if reservation.variant.product.origin == "CLOVER":
            data = {
                "reservation_params": {
                    "origin_id": reservation.origin_id,
                },
            }

            try:
                clover_reservation = CloverReservation(retailer)
                clover_reservation.run(data, "delete")

                messages.success(
                    request,
                    "Reservation cancelled successfully.",
                    extra_tags="success",
                )

                return redirect("index")
            except Exception as e:
                print(e)

        else:
            data = {
                "order_params": {
                    "order": {
                        "location_id": reservation.variant.product.inventory.location.pos_id,
                        "line_items": [
                            {
                                "quantity": str(reservation.quantity),
                                "catalog_object_id": reservation.variant.origin_id,
                            }
                        ],
                        "version": reservation.version,
                    },
                    "idempotency_key": str(uuid.uuid4()),
                },
                "reservation_params": {
                    "order_id": reservation.origin_id,
                    "quantity": reservation.quantity,
                    "product": reservation.variant.id,
                },
            }

            try:
                retailer = reservation.variant.product.inventory.location.retailer
                square_reservation = SquareReservation(retailer)
                square_reservation.run(data, "delete")

                messages.success(
                    request,
                    "Reservation cancelled successfully.",
                    extra_tags="success",
                )

                return redirect("index")
            except Exception as e:
                print(e)


class ReservationsListView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_anonymous:
            return redirect("login")

        template_name = "reservations_list.html"

        upcoming_reservations = Reservation.objects.filter(
            user=request.user,
            time_limit__gte=datetime.datetime.now(),
            status="RESERVED",
        ).order_by("-time_limit")

        return render(
            request,
            template_name,
            {
                "upcoming_reservations": upcoming_reservations,
            },
        )


class ProductListSearchView(TemplateView):
    def get(self, request, **kwargs):
        template_name = "search-products.html"
        search = request.GET.get("search", "").strip()

        products = Product.objects.filter(name__icontains=search).prefetch_related(
            "variants",
            "variants__variantimage_set",
            "wishlist",
        ).all()

        user_wishlist = {}
        if request.user.is_authenticated:
            wishlist = ProductWishlist.objects.filter(user=request.user, product__in=products).all()
            for wish in wishlist:
                user_wishlist[wish.product.id] = True

        return render(
            request,
            template_name,
            {
                "products": products,
                "search": search,
                "user_products_wishlist": user_wishlist
            },
        )


class WishlistView(TemplateView):
    def get(self, request, **kwargs):
        if request.user.is_anonymous:
            return redirect("login")

        template_name = "wishlist.html"

        product_wishlist = Product.objects.filter(wishlist__user=request.user).all()
        retailer_wishlist = Retailer.objects.filter(wishlist__user=request.user).all()

        return render(
            request,
            template_name,
            {
                "product_wishlist": product_wishlist,
                "retailer_wishlist": retailer_wishlist,
                "user_products_wishlist": [product.id for product in product_wishlist],
                "user_retailers_wishlist": [retailer.id for retailer in retailer_wishlist],
            },
        )


@csrf_exempt
def toggler_wishlist(request, **kwargs):
    if request.user.is_anonymous:
        return HttpResponseForbidden()
    request_body = json.loads(request.body)
    _type = request_body.get("type", "product")
    added = False
    if _type == "product":
        product_id = request_body.get("id")
        product = Product.objects.get(id=product_id)

        if product.wishlist.filter(user=request.user).exists():
            ProductWishlist.objects.filter(user=request.user, product=product).delete()
            added = False
        else:
            ProductWishlist.objects.create(user=request.user, product=product)
            added = True
    elif _type == "retailer":
        retailer_id = request_body.get("id")
        retailer = Retailer.objects.get(id=retailer_id)

        if retailer.wishlist.filter(user=request.user).exists():
            RetailerWishlist.objects.filter(user=request.user, retailer=retailer).delete()
            added = False
        else:
            RetailerWishlist.objects.create(user=request.user, retailer=retailer)
            added = True

    return JsonResponse({
        "added": added
    })
