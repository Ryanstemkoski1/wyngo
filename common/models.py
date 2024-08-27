from django.db import models


class BaseTimeModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name=u'Created date',
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=u'Updated date',
        auto_now=True
    )

    class Meta:
        abstract = True
