from django.contrib import admin
from django.urls import path

from portal import accounts, views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", accounts.login_view, name="login"),
    path("logout/", accounts.logout_view, name="logout"),
    path("account/", accounts.account_view, name="account"),
    path("account/password/", accounts.password_change_view, name="password_change"),
    path("manage/users/", accounts.manage_users, name="manage_users"),
    path(
        "manage/users/<int:user_id>/",
        accounts.manage_user_action,
        name="manage_user_action",
    ),
    path("study/", views.study_hub, name="study_hub"),
    path("api/study/", views.study_api, name="study_api"),
    path("api/progress/", views.progress_api, name="progress_api"),
    path("api/progress/update/", views.progress_update_api, name="progress_update_api"),
    path("api/practice/attempt/", views.practice_attempt_api, name="practice_attempt_api"),
    path("practice/", views.practice_hub, name="practice_hub"),
    path("practice/<slug:slug>/", views.practice_detail, name="practice_detail"),
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
