from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='api_register'),
    path('profile/', views.UserProfileView.as_view(), name='api_profile'),
]
