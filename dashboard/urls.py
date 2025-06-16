from django.urls import path
from . import views

from .dash_app import app
app_name = 'dashboard_app'

urlpatterns = [
    path('', views.professor_dashboard_view, name='dashboard'),
]