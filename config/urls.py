from django.contrib import admin
from django.urls import path

from portal.views import home

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
]
