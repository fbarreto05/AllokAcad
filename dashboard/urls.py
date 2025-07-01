from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
    path('', views.professor_dashboard_view, name='professor_dashboard'),
    path('spaces/', views.space_dashboard_view, name='space_dashboard'),
    path('api/update-dashboard-data/', views.update_professor_dashboard_data, name='update_dashboard_data'),
    path('api/update-space-dashboard-data/', views.update_space_dashboard_data, name='update_space_dashboard_data'),
]