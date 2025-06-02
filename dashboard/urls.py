from django.urls import path
from .views import renderDashboard

app_name = 'dashboard_app'

urlpatterns = [
    path('', renderDashboard, name='dashboard'),
]