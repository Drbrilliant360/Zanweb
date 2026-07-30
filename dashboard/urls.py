from django.urls import path
from . import views

urlpatterns = [
    path('volunteer/', views.volunteer_dashboard, name='api_volunteer_dashboard'),
    path('admin/', views.admin_dashboard, name='api_admin_dashboard'),
]
