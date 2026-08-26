from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .webhooks import snippe_webhook

router = DefaultRouter()
router.register('donation-campaigns', views.DonationCampaignViewSet)
router.register('donations', views.DonationViewSet)

urlpatterns = [
    path('webhooks/snippe/', snippe_webhook, name='snippe-webhook'),
    path('', include(router.urls)),
]
