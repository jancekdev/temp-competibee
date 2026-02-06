from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path("settings/", views.account_settings, name="account_settings"),
]
