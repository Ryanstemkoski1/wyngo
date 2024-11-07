import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from accounts.models import User
from common.pos.clover.clover_oauth import CloverOauth
from common.pos.square.square_location import SquareLocation
from common.pos.square.square_oauth import SquareOauth
from inventories.tasks import load_square_inventory, init_retailer
from retailer.models import Retailer, Category
from .forms import RetailerSignupForm

logger = logging.getLogger(__name__)


# Create your views here.
# @user_passes_test(lambda u: u.is_superuser)
def connect_pos(request):
    retailer_id = request.GET.get("i")
    retailer = Retailer.objects.get(pk=retailer_id)

    if retailer.access_token is not None:
        # TODO: Log error
        return redirect("admin:index")

    if retailer.origin == Retailer.CLOVER:
        # Clover Oauth Flow
        redirect_url = CloverOauth.create_clover_oauth_path(retailer, request)
        return redirect(redirect_url)
    elif retailer.origin == Retailer.SQUARE:
        # Square Oauth Flow
        redirect_url = SquareOauth.create_square_oauth_path(retailer)

        if redirect_url == "refresh_token":
            result = SquareOauth.refresh_oauth_session(retailer)
            if result["status"] == 0:
                retailer_id_oauth = result["retailer_id"]
                SquareLocation.fetch_locations(retailer_id=retailer_id_oauth)
                messages.success(request, result["message"])
            else:
                messages.error(request, result["message"])
            return redirect("admin:index")

        return redirect(redirect_url)

    else:
        # TODO: Log error
        pass
    return redirect("admin:retailer_retailer_changelist")


def clover_callback(request, retailer_id):
    merchant_id = request.GET.get("merchant_id")
    code = request.GET.get("code")
    app_id = request.GET.get("client_id")

    result = CloverOauth.create_oauth_session(merchant_id=merchant_id, code=code, app_id=app_id,
                                              retailer_id=retailer_id)
    if result["status"] == 0:
        retailer_id = result["retailer_id"]
        messages.success(request, result["message"])
        messages.warning(request, "You will not be able to see your inventory data until the Wyndo admin "
                                  "checks and approves your retailer account.")

        # After oauth success, send emails to retailer and admin
        retailer = Retailer.objects.get(id=retailer_id)
        request_number = f"#{'{:06d}'.format(retailer_id)}"
        Retailer.register_retailer_email(request_number, retailer.email)

        super_email = (
            User.objects.filter(is_superuser=True).order_by("date_joined").first()
        ).email
        Retailer.register_admin_email(
            super_email, request.build_absolute_uri("/admin/retailer/retailer/")
        )
    else:
        retailer = Retailer.objects.get(id=retailer_id)
        User.objects.filter(email=retailer.email).delete()
        retailer.delete()
        messages.error(request, result["message"])
    return redirect("admin:index")


def square_callback(request):
    state = request.GET.get("state")
    code = request.GET.get("code")

    result = SquareOauth.create_oauth_session(state=state, code=code)
    retailer_id = result["retailer_id"]
    if result["status"] == 0:
        messages.success(request, result["message"])
        messages.warning(request, "You will not be able to see your inventory data until the Wyndo admin "
                                  "checks and approves your retailer account.")

        # After oauth success, send emails to retailer and admin
        retailer = Retailer.objects.get(id=retailer_id)
        request_number = f"#{'{:06d}'.format(retailer_id)}"
        Retailer.register_retailer_email(request_number, retailer.email)

        super_email = (
            User.objects.filter(is_superuser=True).order_by("date_joined").first()
        ).email
        Retailer.register_admin_email(
            super_email, request.build_absolute_uri("/admin/retailer/retailer/")
        )
    else:
        retailer = Retailer.objects.get(id=retailer_id)
        User.objects.filter(email=retailer.email).delete()
        retailer.delete()
        messages.error(request, result["message"])
    return redirect("admin:index")


@user_passes_test(lambda u: u.is_superuser)
def approve_retailer(request):
    retailer_id: str = request.GET.get("i")
    retailer = Retailer.objects.get(pk=retailer_id)

    retailer.status = Retailer.STATUS_APPROVED
    retailer.save()

    url = request.build_absolute_uri(
        reverse("index")
    )

    Retailer.approved_retailer_email(
        retailer.origin, retailer.email, url, retailer.name
    )

    init_retailer.delay(retailer_id=retailer_id, origin=retailer.origin)
    return redirect("admin:retailer_retailer_changelist")


@transaction.atomic
def connect_retailer(request):
    form = RetailerSignupForm(request.POST, request.FILES)
    logger.info(f"Is form valid? {form.is_valid()}")

    if form.is_valid():
        try:
            retailer = form.save()
        except ValidationError as e:
            logger.error(f"Error on validating retailer: {str(e)}")
            messages.error(request, str(e), extra_tags="error")
            return False, None
        except Exception as e:
            logger.error(f"Error saving retailer: {str(e)}")
            return False, None
    else:
        logger.info(f"Errors {form.errors}")
        return False, None

    email = request.POST.get("email")

    # Log user in
    created_retailer_user = User.objects.get(email=email)
    login(request, created_retailer_user)

    origin = request.POST.get("origin")
    super_email = (
        User.objects.filter(is_superuser=True).order_by("date_joined").first()
    ).email
    request_number = f"#{'{:06d}'.format(retailer.pk)}"

    url = f"{reverse('connect_pos')}?i={retailer.id}"
    return True, url


class RetailerSignupView(TemplateView):
    template_name = "register.html"

    def get(self, request, origin, *args, **kwargs):
        categories = Category.objects.all()

        merchant_id = request.GET.get("merchant_id", "")
        app_id = request.GET.get("client_id", "")
        code = request.GET.get("code", "")
        state = request.GET.get("state", "")
        can_continue = True

        if origin.upper() == Retailer.CLOVER:
            retailer = Retailer.objects.filter(
                merchant_id=merchant_id, app_id=app_id
            ).filter()
            if retailer.exists():
                messages.error(
                    request, "The retailer already exist.", extra_tags="error"
                )
                can_continue = False
        elif origin.upper() == Retailer.SQUARE:
            code = None if code == "None" else code
            state = None if state == "None" else state
            if any([code, state]):
                result = SquareOauth.create_oauth_session(state=state, code=code)
                if result["status"] == 0:
                    retailer_id = result["retailer_id"]
                    SquareLocation.fetch_locations(retailer_id=retailer_id)
                    load_square_inventory.delay(retailer_id=retailer_id)
                    messages.success(request, result["message"])
                else:
                    messages.error(request, result["message"])
                return redirect("index")

        return render(
            request,
            self.template_name,
            {
                "categories": categories,
                "merchant_id": merchant_id,
                "app_id": app_id,
                "code": code,
                "origin": origin.upper(),
                "state": state,
                "can_continue": can_continue,
            },
        )

    def post(self, request, *args, **kwargs):
        connected, redirect_url = connect_retailer(request)

        if connected:
            messages.success(
                request, "Retailer created successfully.", extra_tags="success"
            )
            return redirect(redirect_url if redirect_url else "login")
        else:
            messages.error(request, "Retailer creation failed.", extra_tags="error")
            return redirect("sign_up", origin=request.POST.get("origin"))


def delete_retailer(request):
    user = request.user
    Retailer.objects.filter(email=user.email).delete()
    logout(request)
    user.delete()
    messages.success(request, "Your account has been deleted.")
    return redirect("index")


