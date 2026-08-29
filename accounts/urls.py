from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register('admin/users', views.AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='api_register'),
    path('auth/login/', views.LoginView.as_view(), name='api_login'),
    path('auth/logout/', views.LogoutView.as_view(), name='api_logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.MeView.as_view(), name='api_me'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='api_change_password'),
    path('volunteers/', views.VolunteerListView.as_view(), name='api_volunteers'),
    path('volunteers/<int:pk>/', views.VolunteerDetailView.as_view(), name='api_volunteer_detail'),
    path('', include(router.urls)),
]
