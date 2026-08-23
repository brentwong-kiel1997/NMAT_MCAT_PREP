from django.contrib import admin
from django.urls import path

from portal import views

urlpatterns = [
    path("", views.home, name="home"),
    path("diseases/", views.disease_list, name="disease_list"),
    path("diseases/<slug:slug>/", views.disease_detail, name="disease_detail"),
    path("admin/", admin.site.urls),
]
