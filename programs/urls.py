from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('programs', views.ProgramViewSet)
router.register('cohorts', views.CohortViewSet)
router.register('applications', views.ProgramApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
