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
    path('chatbot/', views.ChatbotProxyView.as_view(), name='api_chatbot'),
    path('site-content/', views.SiteContentView.as_view(), name='api_site_content'),
    path('site-content/<str:key>/', views.SiteContentView.as_view(), name='api_site_content_key'),
    path('', include(router.urls)),
]
