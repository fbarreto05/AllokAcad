"""
URL configuration for AllokAcad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('login_validate', views.login_validate, name='login_validate'),
    path('register', views.register, name='register'),
    path('register_validate', views.register_validate, name='register_validate'),
    path('home/<str:userid>', views.home, name='home'),
    path('home/create_ambient/<str:userid>', views.create_ambient, name='create_ambient'),
    path('home/create_ambient_validate/<str:userid>', views.create_ambient_validate, name='create_ambient_validate'),
    path('ambient/<str:ambientid>/<str:userid>', views.ambient, name='ambient'),
    path('ambient/form/<str:ambientid>/<str:userid>', views.ambient_form, name='ambient_form'),
    path('ambient/config/<str:ambientid>/<str:userid>/', views.ambient_config, name='ambient_config'),
    path('ambient/config_validate/<str:ambientid>/<str:userid>/', views.ambient_config_validate, name='ambient_config_validate'),
    path('ambient/solicitations/<str:ambientid>/<str:userid>', views.ambient_solicitations, name='ambient_solicitations'),
    path('ambient/resources/<str:ambientid>/<str:userid>', views.ambient_resources, name='ambient_resources'),
    path('ambient/resources/classes/<str:ambientid>/<str:userid>', views.ambient_classes, name='ambient_classes'),
    path('ambient/resources/classes/create/<str:ambientid>/<str:userid>', views.ambient_create_classes, name='ambient_create_classes'),
    path('ambient/resources/classes/create/validate/<str:ambientid>/<str:userid>', views.ambient_create_classes_validate, name='ambient_create_classes_validate'),
    path('ambient/resources/rooms/<str:ambientid>/<str:userid>', views.ambient_rooms, name='ambient_rooms'),
    path('ambient/resources/rooms/create/<str:ambientid>/<str:userid>', views.ambient_create_rooms, name='ambient_create_rooms'),
    path('ambient/resources/rooms/create/validate/<str:ambientid>/<str:userid>', views.ambient_create_rooms_validate, name='ambient_create_rooms_validate'),
    path('ambient/resources/subjects/<str:ambientid>/<str:userid>', views.ambient_subjects, name='ambient_subjects'),
    path('ambient/resources/subjects/create/<str:ambientid>/<str:userid>', views.ambient_create_subjects, name='ambient_create_subjects'),
    path('ambient/resources/subjects/create/validate/<str:ambientid>/<str:userid>', views.ambient_create_subjects_validate, name='ambient_create_subjects_validate'),
    path('ambient/resources/formations/<str:ambientid>/<str:userid>', views.ambient_formations, name='ambient_formations'),
    path('ambient/resources/formations/create/<str:ambientid>/<str:userid>', views.ambient_create_formations, name='ambient_create_formations'),
    path('ambient/resources/formations/create/validate/<str:ambientid>/<str:userid>', views.ambient_create_formations_validate, name='ambient_create_formations_validate'),
    path('ambient/resources/roomtypes/<str:ambientid>/<str:userid>', views.ambient_roomtypes, name='ambient_roomtypes'),
    path('ambient/resources/roomtypes/create/<str:ambientid>/<str:userid>', views.ambient_create_roomtypes, name='ambient_create_roomtypes'),
    path('ambient/resources/roomtypes/create/validate/<str:ambientid>/<str:userid>', views.ambient_create_roomtypes_validate, name='ambient_create_roomtypes_validate'),
    path('ambient/resources/admtypes/<str:ambientid>/<str:userid>', views.ambient_admtypes, name='ambient_admtypes'),
    path('ambient/resources/admtypes/create/<str:ambientid>/<str:userid>', views.ambient_create_admtypes, name='ambient_create_admtypes'),
    path('ambient/resources/admtypes/create/validate/<str:ambientid>/<str:userid>', views.ambient_create_admtypes_validate, name='ambient_create_admtypes_validate'),
    path('ambient/profile/<str:ambientid>/<str:userid>', views.ambient_profile, name='ambient_profile'),
    path('ambient/members/<str:ambientid>/<str:userid>', views.ambient_members, name='ambient_members'),

    ]
