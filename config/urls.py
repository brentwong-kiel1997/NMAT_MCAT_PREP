from django.contrib import admin
from django.urls import path

from portal import views

urlpatterns = [
    path("", views.home, name="home"),
    path("study/", views.study_hub, name="study_hub"),
    path("api/study/", views.study_api, name="study_api"),
    path("subjects/", views.subject_list, name="subject_list"),
    path("subjects/<slug:slug>/", views.subject_detail, name="subject_detail"),
    path("nmat/", views.nmat_hub, name="nmat_hub"),
    path("nmat/<slug:slug>/", views.nmat_subject, name="nmat_subject"),
    path("mcat/", views.mcat_hub, name="mcat_hub"),
    path("mcat/<slug:slug>/", views.mcat_section, name="mcat_section"),
    path("diseases/", views.disease_list, name="disease_list"),
    path("diseases/<slug:slug>/", views.disease_detail, name="disease_detail"),
    path("admin/", admin.site.urls),
]
