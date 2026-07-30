from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('donation-campaigns', views.DonationCampaignViewSet)
router.register('donations', views.DonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
