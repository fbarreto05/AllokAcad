from django.urls import path
from . import views
from dashboard import dash_app

app_name = 'dashboard_app'

urlpatterns = [
    path('', views.professor_dashboard_view, name='dashboard'),
]