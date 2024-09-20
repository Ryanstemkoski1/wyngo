from django import forms
from django.conf import settings
from django.core import validators
from common.retailer_utils import RetailerUtils
from wyndo.settings import (
    CLOVER_API_SECRET,
    SQUARE_API_SECRET,
    SQUARE_API_KEY,
    CLOVER_API_KEY,
)
from .models import Retailer, Category


class RetailerForm(forms.ModelForm):
    class Meta:
        model = Retailer
        fields = "__all__"

    def save(self, commit=True):
        instance: Retailer = super(RetailerForm, self).save(commit=False)
        instance.app_id = (
            settings.CLOVER_API_KEY
            if instance.origin == Retailer.CLOVER
            else settings.SQUARE_API_KEY
        )
        instance.app_secret = (
            settings.CLOVER_API_SECRET
            if instance.origin == Retailer.CLOVER
            else settings.SQUARE_API_SECRET
        )

        if instance is not None:
            if "merchant_id" in self.changed_data:
                instance.disconnect_retailer()

        instance.save()
        return instance


class RetailerSignupForm(forms.ModelForm):
    name = forms.CharField(max_length=128, required=True)
    description = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField(required=True, validators=[validators.validate_email])
    code = forms.CharField(max_length=128, required=False)
    merchant_id = forms.CharField(max_length=128, required=False)
    app_id = forms.CharField(max_length=128, required=False)
    origin = forms.CharField(max_length=128, required=True)
    image = forms.ImageField(required=True)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple
    )

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            try:
                if image.content_type == "image/gif":
                    raise forms.ValidationError("Images .gif are not allowed")

            except Exception as e:
                raise forms.ValidationError("Invalid file. Error: {}".format(e))
        return image

    def save(self, commit=True):
        instance: Retailer = super(RetailerSignupForm, self).save(commit=False)
        if instance is not None:
            instance.merchant_id = (
                instance.merchant_id if instance.merchant_id else None
            )
            if instance.origin == Retailer.CLOVER:
                instance.app_id = CLOVER_API_KEY
                instance.app_secret = CLOVER_API_SECRET
            elif instance.origin == Retailer.SQUARE:
                instance.app_id = SQUARE_API_KEY
                instance.app_secret = SQUARE_API_SECRET
            instance.save()

            categories = Category.objects.filter(pk=int(self.data.get("category")))
            for category in categories:
                instance.category.add(category)

            instance.save()

            # Check retailer account to promote
            RetailerUtils.check_and_promote_retailer_admin_account(instance.email)

        return instance

    class Meta:
        model = Retailer
        fields = [
            "name",
            "description",
            "email",
            "code",
            "merchant_id",
            "app_id",
            "origin",
            "image",
            "category",
        ]
