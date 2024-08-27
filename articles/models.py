from django.db import models
from common.models import BaseTimeModel
from ckeditor.fields import RichTextField
from django.template.defaultfilters import truncatechars


class Article(BaseTimeModel):
    title = models.CharField(max_length=150, verbose_name='title')
    slug = models.SlugField(max_length=150, verbose_name='slug', unique=True)
    content = RichTextField(config_name='content')
    
    @property
    def short_content(self):
        return truncatechars(self.content, 130)

    def update_article(
        self,
        title: str,
        slug: str,
        content: str,
    ):
        self.title = title
        self.slug = slug
        self.content = content

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        