from django.urls import path
from . import views

app_name = 'dashboard_app'

urlpatterns = [
    path('', views.professor_dashboard_view, name='dashboard'),
]