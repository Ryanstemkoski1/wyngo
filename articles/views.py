import random

from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from faker import Faker
from django.core.paginator import Paginator

import random
from retailer.models import Category, Retailer
from django.db.models import Q, Count
from .models import Article


# Create your views here.


class ArticleDetailsView(DetailView):
    template_name = "article.html"
    model = Article
