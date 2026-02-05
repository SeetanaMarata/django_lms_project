# materials/urls_subscriptions.py
from django.urls import path

from .views_subscription import SubscriptionAPIView

urlpatterns = [
    path("", SubscriptionAPIView.as_view(), name="subscription"),
]
