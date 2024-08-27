from django.urls import path
from django.conf.urls.static import static
from .views import (
    ArticleDetailsView,
)
from django.conf import settings

urlpatterns = [
    path(
        "<str:slug>",
        ArticleDetailsView.as_view(template_name="article.html"),
        name="article-details",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
