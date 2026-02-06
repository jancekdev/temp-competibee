from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("checkout/<str:price_id>/", views.create_checkout_session, name="checkout"),
    path("customer-portal/", views.customer_portal, name="customer-portal"),
    path("webhook/", views.stripe_webhook, name="webhook"),
]
