# payments/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CreateCheckoutSession,
    StripeWebhookView,
    PaymentViewSet,
    PaymentSuccessView,
    PaymentCancelView,
)

router = DefaultRouter()
router.register("history", PaymentViewSet, basename="payment")

urlpatterns = [
    path("create-checkout/", CreateCheckoutSession.as_view()),
    path("webhook/", StripeWebhookView.as_view()),
    path("success/", PaymentSuccessView.as_view()),
    path("cancel/", PaymentCancelView.as_view()),
    path("", include(router.urls)),
]