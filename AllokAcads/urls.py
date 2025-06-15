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
from django.urls import path, include
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('login_validate', views.login_validate, name='login_validate'),
    path('register', views.register, name='register'),
    path('register_validate', views.register_validate, name='register_validate'),
    path('home', views.home, name='home'),
    path('home/profile/', views.profile, name='profile'),
    path('home/profile/edit', views.profile_edit, name='profile_edit'),
    path('home/profile/edit/validate', views.profile_edit_validate, name='profile_edit_validate'),
    path('home/create_ambient', views.create_ambient, name='create_ambient'),
    path('home/create_ambient_validate', views.create_ambient_validate, name='create_ambient_validate'),
    path('home/enter_ambient', views.enter_ambient, name='enter_ambient'),
    path('ambient/<str:ambientid>', views.ambient, name='ambient'),
    path('ambient/form/validate/<str:ambientid>', views.ambient_form_validate, name='ambient_form_validate'),
    path('ambient/config/<str:ambientid>', views.ambient_config, name='ambient_config'),
    path('ambient/delete/<str:ambientid>', views.ambient_delete, name='ambient_delete'),
    path('ambient/profile/delete', views.profile_delete, name='profile_delete'),
    path('ambient/config_validate/<str:ambientid>', views.ambient_config_validate, name='ambient_config_validate'),
    path('ambient/solicitations/<str:ambientid>', views.ambient_solicitations, name='ambient_solicitations'),
    path('ambient/solicitations/accept/<str:memberid>/<str:ambientid>', views.accept_solicitation, name='accept_solicitation'),
    path('ambient/solicitations/refuse/<str:memberid>/<str:ambientid>', views.refuse_solicitation, name='refuse_solicitation'),
    path('ambient/resources/<str:ambientid>', views.ambient_resources, name='ambient_resources'),

    path('ambient/resources/classes/<str:ambientid>', views.ambient_classes, name='ambient_classes'),
    path('ambient/resources/classes/create/<str:ambientid>', views.ambient_create_classes, name='ambient_create_classes'),
    path('ambient/resources/classes/create/validate/<str:ambientid>', views.ambient_create_classes_validate, name='ambient_create_classes_validate'),
    path('ambient/resources/classes/edit/<int:classid>/<str:ambientid>', views.ambient_edit_classes, name='ambient_edit_classes'),
    path('ambient/resources/classes/edit/<int:classid>/validate/<str:ambientid>', views.ambient_edit_classes_validate, name='ambient_edit_classes_validate'),
    path('ambient/resources/classes/delete/<int:classid>/<str:ambientid>', views.ambient_delete_classes, name='ambient_delete_classes'),

    path('ambient/resources/rooms/<str:ambientid>', views.ambient_rooms, name='ambient_rooms'),
    path('ambient/resources/rooms/create/<str:ambientid>', views.ambient_create_rooms, name='ambient_create_rooms'),
    path('ambient/resources/rooms/create/validate/<str:ambientid>', views.ambient_create_rooms_validate, name='ambient_create_rooms_validate'),
    path('ambient/resources/rooms/edit/<int:roomid>/<str:ambientid>', views.ambient_edit_rooms, name='ambient_edit_rooms'),
    path('ambient/resources/rooms/edit/validate/<int:roomid>/<str:ambientid>', views.ambient_edit_rooms_validate, name='ambient_edit_rooms_validate'),
    path('ambient/resources/rooms/delete/<int:roomid>/<str:ambientid>', views.ambient_delete_rooms, name='ambient_delete_rooms'),

    path('ambient/resources/subjects/<str:ambientid>', views.ambient_subjects, name='ambient_subjects'),
    path('ambient/resources/subjects/create/<str:ambientid>', views.ambient_create_subjects, name='ambient_create_subjects'),
    path('ambient/resources/subjects/create/validate/<str:ambientid>', views.ambient_create_subjects_validate, name='ambient_create_subjects_validate'),
    path('ambient/resources/subjects/edit/<int:subjectid>/<str:ambientid>', views.ambient_edit_subjects, name='ambient_edit_subjects'),
    path('ambient/resources/subjects/edit/validate/<int:subjectid>/<str:ambientid>', views.ambient_edit_subjects_validate, name='ambient_edit_subjects_validate'),
    path('ambient/resources/subjects/delete/<int:subjectid>/<str:ambientid>', views.ambient_delete_subjects, name='ambient_delete_subjects'),

    path('ambient/resources/formations/<str:ambientid>', views.ambient_formations, name='ambient_formations'),
    path('ambient/resources/formations/create/<str:ambientid>', views.ambient_create_formations, name='ambient_create_formations'),
    path('ambient/resources/formations/create/validate/<str:ambientid>', views.ambient_create_formations_validate, name='ambient_create_formations_validate'),
    path('ambient/resources/formations/edit/<int:formationid>/<str:ambientid>', views.ambient_edit_formations, name='ambient_edit_formations'),
    path('ambient/resources/formations/edit/validate/<int:formationid>/<str:ambientid>', views.ambient_edit_formations_validate, name='ambient_edit_formations_validate'),
    path('ambient/resources/formations/delete/<int:formationid>/<str:ambientid>', views.ambient_delete_formations, name='ambient_delete_formations'),

    path('ambient/resources/roomtypes/<str:ambientid>', views.ambient_roomtypes, name='ambient_roomtypes'),
    path('ambient/resources/roomtypes/create/<str:ambientid>', views.ambient_create_roomtypes, name='ambient_create_roomtypes'),
    path('ambient/resources/roomtypes/create/validate/<str:ambientid>', views.ambient_create_roomtypes_validate, name='ambient_create_roomtypes_validate'),
    path('ambient/resources/roomtypes/edit/<int:roomid>/<str:ambientid>', views.ambient_edit_roomtypes, name='ambient_edit_roomtypes'),
    path('ambient/resources/roomtypes/edit/validate/<int:roomid>/<str:ambientid>', views.ambient_edit_roomtypes_validate, name='ambient_edit_roomtypes_validate'),
    path('ambient/resources/roomtypes/delete/<int:roomid>/<str:ambientid>', views.ambient_delete_roomtypes, name='ambient_delete_roomtypes'),

    path('ambient/resources/admtypes/<str:ambientid>', views.ambient_admtypes, name='ambient_admtypes'),
    path('ambient/resources/admtypes/create/<str:ambientid>', views.ambient_create_admtypes, name='ambient_create_admtypes'),
    path('ambient/resources/admtypes/create/validate/<str:ambientid>', views.ambient_create_admtypes_validate, name='ambient_create_admtypes_validate'),
    path('ambient/resources/admtypes/edit/<int:admtypeid>/<str:ambientid>', views.ambient_edit_admtypes, name='ambient_edit_admtypes'),
    path('ambient/resources/admtypes/edit/validate/<int:admtypeid>/<str:ambientid>', views.ambient_edit_admtypes_validate, name='ambient_edit_admtypes_validate'),
    path('ambient/resources/admtypes/delete/<int:admtypeid>/<str:ambientid>', views.ambient_delete_admtypes, name='ambient_delete_admtypes'),

    path('ambient/profile/<str:ambientid>', views.ambient_profile, name='ambient_profile'),
    path('ambient/profile/edit/<str:ambientid>', views.ambient_profile_edit, name='ambient_profile_edit'),
    path('ambient/profile/edit/validate/<str:ambientid>', views.ambient_profile_edit_validate, name='ambient_profile_edit_validate'),
    path('ambient/members/<str:ambientid>', views.ambient_members, name='ambient_members'),
    path('ambient/professor_true/<str:memberid>/<str:ambientid>', views.professor_true, name='professor_true'),
    path('ambient/professor_false/<str:memberid>/<str:ambientid>', views.professor_false, name='professor_false'),
    path('ambient/change_position/<str:memberid>/<str:ambientid>', views.change_position, name='change_position'),
    path('ambient/remove_member/<str:memberid>/<str:ambientid>', views.remove_member, name='remove_member'),
    path('ambient/change_position_validate/<str:memberid>/<str:ambientid>', views.change_position_validate, name='change_position_validate'),
    path('ambient/run_atribuition/<str:ambientid>', views.run_atribuition, name='run_atribuition'),
    path('ambient/run_alocation/<str:ambientid>', views.run_alocation, name='run_alocation'),
    path('dashboard/', include('dashboard.urls')),

    path('home/exit', views.exit, name='exit'),
    ]
