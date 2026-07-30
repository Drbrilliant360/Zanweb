from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('events', views.EventViewSet)
router.register('event-registrations', views.EventRegistrationViewSet)
router.register('impact-logs', views.ImpactLogViewSet, basename='impact-log')
router.register('badges', views.BadgeViewSet)
router.register('certificates', views.CertificateViewSet, basename='certificate')
router.register('messages', views.CoordinatorMessageViewSet, basename='message')

urlpatterns = [
    path('my-registrations/', views.MyEventRegistrationsView.as_view(), name='api_my_registrations'),
    path('my-badges/', views.MyBadgesView.as_view(), name='api_my_badges'),
    path('', include(router.urls)),
]
