from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet


class NonEmptyInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if not any(form.cleaned_data for form in self.forms if not form.cleaned_data.get("DELETE", False)):
            raise ValidationError("At least one child record is required.")
