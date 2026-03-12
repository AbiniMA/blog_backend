from django.urls import path
from .views import google_login, get_user, all_users

urlpatterns = [
    path("google-login/", google_login),
    path("user/", get_user),
    path("users/", all_users),
]