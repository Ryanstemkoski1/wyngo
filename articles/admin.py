from datetime import datetime
from urllib.parse import urlencode

from django import forms
from django.contrib import admin
from django.urls import reverse, path
from django.utils.html import format_html

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "slug",
        "short_content",
        "created_at",
        "updated_at",
    )
    list_display_links = ("title",)
    prepopulated_fields = {"slug": ["title"]}
    fields = ["title","slug", "content"]
    
    def add_view(self, request, form_url="", extra_context=None):
        prepopulated_fields = {"slug": ["title"]}
        self.readonly_fields = []
        return super(ArticleAdmin, self).add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.prepopulated_fields = {}
        self.readonly_fields = ["slug"]
        return super(ArticleAdmin, self).change_view(request, object_id, form_url, extra_context)
