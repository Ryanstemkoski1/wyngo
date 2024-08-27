from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import Q
from multiupload.fields import MultiMediaField

from .models import Product, Variant, VariantImage


class VariantForm(forms.ModelForm):
    image = MultiMediaField(
        min_num=0, max_num=10, max_file_size=1024 * 1024 * 5, media_type="image"
    )

    def __init__(self, *args, **kwargs):
        super(VariantForm, self).__init__(*args, **kwargs)
        instance = self.instance
        if instance.id:
            self.fields["image"] = MultiMediaField(
                min_num=0,
                max_num=10 - VariantImage.objects.filter(variant=instance).count(),
                max_file_size=1024 * 1024 * 5,
                media_type="image",
            )

    def save(self, commit=False):
        instance: Variant = super(VariantForm, self).save(commit=False)

        if "is_modified_by_admin" not in self.changed_data:
            instance.is_modified_by_admin = (
                False
                if "description" in self.changed_data
                and self.cleaned_data.get("description") == ""
                else True
            )
        else:
            instance.is_modified_by_admin = self.cleaned_data["is_modified_by_admin"]

        instance.save()

        if VariantImage.objects.filter(variant=instance).count() <= 10:
            for image in self.cleaned_data.get("image"):
                VariantImage.objects.create(variant=instance, image=image)
        return instance

    class Meta:
        model = Variant
        fields = "__all__"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["category"].initial = self.instance.category

    def save(self, commit=True):
        instance: Product = super(ProductForm, self).save(commit=False)

        if "is_modified_by_admin" not in self.changed_data:
            instance.is_modified_by_admin = True
        else:
            instance.is_modified_by_admin = self.cleaned_data["is_modified_by_admin"]

        instance.save()
        return instance


class CategoryForm(forms.ModelForm):
    product = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=FilteredSelectMultiple("Products", is_stacked=False),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["product"].queryset = Product.objects.filter(
                Q(category__isnull=True) | Q(category=self.instance)
            )
            self.fields["product"].initial = self.instance.product_set.all()
        else:
            self.fields["product"].queryset = Product.objects.filter(
                category__isnull=True
            )

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        instance.save()

        current_products = self.cleaned_data.get("product")
        for product in current_products:
            product.category = instance
            product.save()

        if self.instance.pk:
            old_products = self.instance.product_set.all()
            removed_products = old_products.difference(current_products)
            for product in removed_products:
                product.category = None
                product.save()

        return instance
