from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('contact-messages', views.ContactMessageViewSet)
router.register('newsletter', views.NewsletterSubscriberViewSet)
router.register('partners', views.PartnerViewSet, basename='partner')
router.register('stories', views.StoryViewSet, basename='story')
router.register('gallery', views.GalleryImageViewSet)
router.register('faq', views.FAQViewSet)
router.register('org-stats', views.OrgStatViewSet)

urlpatterns = [
    path('faq/match/', views.FAQMatchView.as_view(), name='api_faq_match'),
    path('', include(router.urls)),
]
