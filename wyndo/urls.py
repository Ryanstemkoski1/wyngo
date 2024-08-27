from django.contrib import admin

"""
URL configuration for wyndo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("shopper.urls")),
    path("", include("accounts.urls")),
    path("inventory/", include("inventories.urls")),
    path("retailer/", include("retailer.urls")),
    path("", include("articles.urls")),
]

admin.site.site_header = "Wyndo Admin Panel"

admin.site.site_title = "Wyndo"

admin.site.index_title = "Welcome to Wyndo Administration Panel"
