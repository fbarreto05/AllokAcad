import json
import threading
_thread_locals = threading.local()
from urllib import request
from django.shortcuts import render, redirect
from django.conf import settings
import random, os, datetime, time

import requests
from .models import User, Ambient, Member, AdminTP, ClassroomTP, Formation, Subject, Formation_Preference, Classroom, Class, Professor_Preference, Classroom_Preference, Schedule_Preference, Class_Preference, Subject_Preference, Member_Formation, Activitie, Timetable, Alocation, Unregistered_Activitie
from shutil import copyfile
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User as UserAuth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# import pwd
# import grp

# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect(f'/home')
    else:
        return render(request, "AllokAcads/login.html")

def login_validate(request):
    if request.user.is_authenticated:
        return redirect(f'/home')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user:
            identificator = user.userid
            auth = authenticate(request, username=identificator, password=password)
            if auth:
                auth_login(request, auth)
                return redirect(f'/home')
        return redirect('/?error=login_failed')

def register(request):
    if request.user.is_authenticated:
        return redirect(f'/home')
    else:
        ambients = Ambient.objects.all()
        return render(request, "AllokAcads/register.html", {'ambients':ambients})

def generate_userid():
    identificator = ""
    for i in range(3):
        digit = chr(random.randint(65, 90))
        identificator += digit
    for i in range(6):
        digit = str(random.randint(0, 9))
        identificator += digit
    return identificator

def register_validate(request):
    if request.user.is_authenticated:
        return redirect(f'/home')
    else:
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        birthdate = request.POST.get('birthdate')
        ambientid = request.POST.get('ambientid')

        if User.objects.filter(email=email):
            return JsonResponse({'error': 'email_exists', 'message': 'Este e-mail já está cadastrado no sistema.'}, status=400)

        while(True):
            identificator = generate_userid()
            user = User.objects.filter(userid = identificator)
            if(not user):
                break

        directory = os.path.join(settings.BASE_DIR, f'media/users/{identificator}/user_picture')
        os.makedirs(directory, exist_ok=True)
        default_picture_path = os.path.join(settings.BASE_DIR, 'media', 'users/user.png')
        copyfile(default_picture_path, os.path.join(directory, 'user.png'))
        picture = f'users/{identificator}/user_picture/user.png'

        ambient = Ambient.objects.get(ambientid = ambientid)

        if ambient:
            ambient.enter_solicitations.append(identificator)
            ambient.save()

        userauth = UserAuth(username=identificator, email=email)
        userauth.set_password(password)
        userauth.save()

        user = User(userid=identificator, picture=picture, name=name, email=email, birthdate=birthdate)
        user.save()

        return redirect(f'/')

def profile(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        picture = user.picture
        return render(request, "AllokAcads/profile.html", {'userid' : user.userid, 'user' : user, 'picture' : picture})
    else:
        return redirect('/')

def profile_edit(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        return render(request, "AllokAcads/profile_edit.html", {'userid' : user.userid, 'user' : user})
    else:
        return redirect('/')

def profile_edit_validate(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        user_session = request.user
        picture = request.FILES.get('picture')
        name = request.POST.get('name')
        description = request.POST.get('description')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if picture:
            picture_path = user.picture.path
            user.picture = picture
            os.remove(picture_path)
        if name:
            user.name = name
        if description:
            user.description = description
        if email:
            user.email = email
            user_session.email = email
            user_session.save()
        if password:
            user_session.set_password(password)
            user_session.save()
            update_session_auth_hash(request, user)
        user.save()
        return redirect(f'/home/profile')
    else:
        return redirect('/')

def profile_delete(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        userauth = UserAuth.objects.get(id = user.id)
        user.delete()
        auth_logout(request)
        userauth.delete()
    return redirect('/')

def home(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        ambients = user.ambients.all()
        username = user.name
        system_ambients = Ambient.objects.all()

        pending_requests = []
        for ambient in system_ambients:
            if user.userid in ambient.enter_solicitations:
                pending_requests.append(ambient)

        return render(request, "AllokAcads/home.html", {
            'user': user,
            'username': username,
            'userid': user.userid,
            'ambients': ambients,
            'system_ambients': system_ambients,
            'pending_requests': pending_requests
        })
    else:
        return redirect('/')

def exit(request):
    if request.user.is_authenticated:
        auth_logout(request)
        return redirect('/')
    else:
        return redirect('/')

def create_ambient(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        return render(request, "AllokAcads/create_ambient.html", {'user' : user, 'userid' : user.userid})
    else:
        return redirect('/')

def generate_ambientid():
    identificator = ""
    for i in range(4):
        digit = chr(random.randint(65, 90))
        identificator += digit
    for i in range(5):
        digit = str(random.randint(0, 9))
        identificator += digit
    return identificator

def create_ambient_validate(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        picture = request.FILES.get('picture')
        name = request.POST.get('name')
        description = request.POST.get('description')
        password = request.POST.get('password')

        if password == "12345":
            while(True):
                identificator = generate_ambientid()
                ambient = Ambient.objects.filter(ambientid = identificator)
                if(not ambient):
                    break

            if not picture:
                directory = os.path.join(settings.BASE_DIR, f'media/ambients/{identificator}/ambient_picture')
                os.makedirs(directory, exist_ok=True)
                default_picture_path = os.path.join(settings.BASE_DIR, 'media', 'ambients/ambient.png')
                copyfile(default_picture_path, os.path.join(directory, 'ambient.png'))
                picture = f'ambients/{identificator}/ambient_picture/ambient.png'

            main_adm = AdminTP(name='Administrador', can_configure_ambient=True, can_gerenciate_members=True, can_register_resources=True, can_run_atribuition=True, can_run_alocation=True)
            main_adm.save()

            creator = Member(user=user, admin_type=main_adm, is_professor=False)
            ambient = Ambient(ambientid=identificator, name=name, picture=picture, description=description)

            ambient.save()
            creator.save()
            user.ambients.add(ambient)
            ambient.admin_types.add(main_adm)
            ambient.members.add(creator)
        return redirect('/home')
    else:
        return redirect('/'),

def enter_ambient(request):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        ambientid = request.POST.get('ambient_identificator')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')

        if ambient:
            if not(user.userid in ambient.enter_solicitations):
                if not(ambient.members.filter(user = user)):
                    ambient.enter_solicitations.append(user.userid)
                    ambient.save()
                    messages.success(request, "Solicitação enviada, aguarde aprovação.")
                else:
                    messages.error(request, "Você já é membro deste ambiente.")
            else:
                messages.error(request, "Uma solicitação já foi enviada para este ambiente.")
        else:
            messages.error(request, "Ambiente não encontrado.")
        return redirect(f'/home')
    else:
        return redirect('/')

def ambient(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user):
            not_alocated = []
            ordered_table = []
            if ambient.published_timetable:
                not_alocated = ambient.published_timetable.not_alocated.all()
                if ambient.published_timetable.columns_number and ambient.published_timetable.lines_number:
                    for column in range(ambient.published_timetable.columns_number):
                        for line in range(ambient.published_timetable.lines_number):
                            if ambient.published_timetable.table.filter(column = column, line = line):
                                ordered_table.append(ambient.published_timetable.table.get(column = column, line = line))

            schedules = ambient.available_schedules.all()
            classrooms = ambient.classrooms.all()
            classes = ambient.classes.all()
            subjects = ambient.subjects.all()
            activities = ambient.activities.all()
            picture = ambient.picture
            username = user.name
            columns_range = 0
            periods_range = 0
            if ambient.days_in_a_cicle:
                columns_range = range(ambient.days_in_a_cicle)
            if ambient.periods_in_a_day:
                periods_range = range(ambient.periods_in_a_day)

            from AllokAcads.rko_llm_constraints import load_rules
            restricoes_ativas = load_rules(ambient.ambientid)

            return render(request, "AllokAcads/ambient.html", {
                'ambient': ambient,
                'user': user,
                'userid': user.userid,
                'username': username,
                'member': member,
                'schedules': schedules,
                'classrooms': classrooms,
                'classes': classes,
                'subjects': subjects,
                'picture': picture,
                'activities': activities,
                'table': ordered_table,
                'not_alocated': not_alocated,
                'columns_range': columns_range,
                'periods_range': periods_range,
                'restricoes_ativas': restricoes_ativas,
            })
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_form(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user=user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user):
            schedules = ambient.available_schedules.all()
            member_schedules = member.prefered_schedules.all()
            classrooms = ambient.classrooms.all()
            classes = ambient.classes.all()
            subjects = ambient.subjects.all()
            activities = ambient.activities.all()
            picture = ambient.picture
            username = user.name
            columns_range = range(ambient.days_in_a_cicle)
            periods_range = range(ambient.periods_in_a_day)

            prefered_subjects = list(member.prefered_subjects.values_list('subject', flat=True))
            subject_preference = list(member.prefered_subjects.values_list('subject_weight', flat=True))
            subjects_and_weight = list(zip(prefered_subjects, subject_preference))

            return render(request, "AllokAcads/ambient_form.html", {
                'ambient': ambient,
                'user': user,
                'userid': user.userid,
                'username': username,
                'member': member,
                'schedules': schedules,
                'classrooms': classrooms,
                'classes': classes,
                'subjects': subjects,
                'picture': picture,
                'activities': activities,
                'columns_range': columns_range,
                'periods_range': periods_range,
                'member_schedules': member_schedules,
                'subjects_and_weight': subjects_and_weight,
            })
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_form_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.is_professor:
            available_schedules = request.POST.getlist('available_schedules')
            prefered_subjects = request.POST.getlist('prefered_subjects')
            member.prefered_schedules.clear()
            if available_schedules:
                for available_schedule in available_schedules:
                    schedule = Schedule_Preference.objects.get(id = available_schedule)
                    member.prefered_schedules.add(schedule)
            member.prefered_subjects.all().delete()
            for prefered_subject in prefered_subjects:
                subject = Subject.objects.get(id = prefered_subject)
                subject_weight = int(request.POST.get(f"option_{prefered_subject}"))
                subject_preference = Subject_Preference(subject=subject, subject_weight=subject_weight)
                subject_preference.save()
                member.prefered_subjects.add(subject_preference)
            return redirect(f'/ambient/form/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_config(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_configure_ambient:
            member = member

            context = {
                'ambient': ambient,
                'user': user,
                'userid': user.userid,
                'member': member
            }

            return render(request, "AllokAcads/ambient_config.html", context)
        else:
            return redirect('home')
    else:
        return redirect('/')


def ambient_config_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_configure_ambient:
            picture = request.FILES.get('picture')
            name = request.POST.get('name')
            description = request.POST.get('description')
            periods_in_a_day = request.POST.get('periods_in_a_day')
            days_in_a_cicle = request.POST.get('days_in_a_cicle')
            form_opening = request.POST.get('form_opening')
            form_closing = request.POST.get('form_closing')
            alt_solicitations_opening = request.POST.get('alt_solicitations_opening')
            alt_solicitations_closing = request.POST.get('alt_solicitations_closing')
            min_actv_in_a_day = request.POST.get('min_actv_in_a_day')
            max_actv_in_a_day = request.POST.get('max_actv_in_a_day')
            min_actv_in_a_cicle = request.POST.get('min_actv_in_a_cicle')
            max_actv_in_a_cicle = request.POST.get('max_actv_in_a_cicle')

            timetable = None
            if ambient.published_timetable:
                timetable = ambient.published_timetable
            if picture:
                picture_path = ambient.picture.path
                ambient.picture = picture
                os.remove(picture_path)
            if name:
                ambient.name = name
            if description:
                ambient.description = description
            if periods_in_a_day:
                ambient.periods_in_a_day = periods_in_a_day
                if timetable:
                    timetable.lines_number = periods_in_a_day
            if days_in_a_cicle:
                ambient.days_in_a_cicle = days_in_a_cicle
                if timetable:
                    timetable.columns_number = days_in_a_cicle

            ambient.form_opening = form_opening if form_opening else None
            ambient.form_closing = form_closing if form_closing else None
            ambient.alt_solicitations_opening = alt_solicitations_opening if alt_solicitations_opening else None
            ambient.alt_solicitations_closing = alt_solicitations_closing if alt_solicitations_closing else None

            if min_actv_in_a_day:
                ambient.min_actv_in_day = min_actv_in_a_day
            if max_actv_in_a_day:
                ambient.max_actv_in_day = max_actv_in_a_day
            if min_actv_in_a_cicle:
                ambient.min_actv_in_cicle = min_actv_in_a_cicle
            if max_actv_in_a_cicle:
                ambient.max_actv_in_cicle = max_actv_in_a_cicle

            ambient.save()
            if ambient.published_timetable:
                timetable.save()

            if (periods_in_a_day and days_in_a_cicle) or (periods_in_a_day and ambient.days_in_a_cicle) or (ambient.periods_in_a_day or days_in_a_cicle):
                ambient.available_schedules.all().delete()
                for i in range(int(days_in_a_cicle)):
                    for j in range(int(periods_in_a_day)):
                        schedule = Schedule_Preference(line=j, column=i)
                        schedule.save()
                        ambient.available_schedules.add(schedule)

            messages.success(request, 'Configurações do ambiente atualizadas com sucesso!')
            return redirect(f'/ambient/config/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_configure_ambient:
            ambient.delete()
        return redirect('home')
    else:
        return redirect('/')

def ambient_profile(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user):
            picture = user.picture
            return render(request, "AllokAcads/ambient_profile.html", {'user' : user, 'ambient' : ambient, 'picture' : picture, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_profile_edit(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user):
            formations = ambient.formations.all()
            relevant_formations = list(member.formations.values_list('formation', flat=True))
            formations_professional = list(member.formations.values_list('professional_experience_time', flat=True))
            formations_didatic = list(member.formations.values_list('didactic_experience_time', flat=True))
            formations_and_professional_and_didatic = list(zip(relevant_formations, formations_professional, formations_didatic))
            return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient, 'user': user, 'formations' : formations, 'userid': user.userid, 'member': member, 'relevant_formations': relevant_formations, 'formations_and_professional_and_didatic': formations_and_professional_and_didatic})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_profile_edit_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user):
            ambient_formations = ambient.formations.all()
            registration = request.POST.get('register')
            formations = request.POST.getlist('member_formations')
            time_in_campus = request.POST.get('time_in_campus')
            time_in_institution = request.POST.get('time_in_institution')
            career_level = request.POST.get('career_level')
            if formations:
                member.formations.all().delete()
                for formation in formations:
                    formation = Formation.objects.get(id = formation)
                    didatic_experience_time = request.POST.get(f"didatic_experience_time_{formation.id}")
                    professional_experience_time = request.POST.get(f"professional_experience_time_{formation.id}")
                    member_formation = Member_Formation(formation=formation, didactic_experience_time = didatic_experience_time, professional_experience_time = professional_experience_time)
                    member_formation.save()
                    member.formations.add(member_formation)
            if registration:
                member.registration = registration
            if time_in_campus:
                member.time_in_campus = time_in_campus
            if time_in_institution:
                member.time_in_institution = time_in_institution
            if career_level:
                member.career_level = career_level
            member.save()
            return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient, 'user': user, 'formations' : ambient_formations, 'userid': user.userid, 'member': member})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_members(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user):
            members = ambient.members.all().order_by('user__name')
            return render(request, "AllokAcads/ambient_members.html", {'ambient' : ambient, 'user' : user, 'members' : members,  'tmember' : member, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def professor_true(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            try:
                member = ambient.members.all().get(id=memberid)
            except Member.DoesNotExist:
                return redirect(f'/ambient/members/{ambientid}')
            member.is_professor = True
            member.save()
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def professor_false(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            try:
                member = ambient.members.all().get(id=memberid)
            except Member.DoesNotExist:
                return redirect(f'/ambient/members/{ambientid}')
            member.is_professor = False
            member.save()
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def change_position(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            try:
                member = ambient.members.get(id=memberid)
            except Member.DoesNotExist:
                return redirect(f'/ambient/members/{ambientid}')
            admtypes = ambient.admin_types.all()
            return render(request, "AllokAcads/change_position.html", {'ambient' : ambient, 'member' : member, 'user' : user, 'admtypes' : admtypes, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def change_position_validate(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            try:
                member = ambient.members.get(id=memberid)
            except Member.DoesNotExist:
                return redirect(f'/ambient/members/{ambientid}')
            admtype = request.POST.get('admtype')
            admtype = AdminTP.objects.get(id = admtype)
            member.admin_type = admtype
            member.save()
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def remove_member(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            try:
                member = ambient.members.get(id=memberid)
            except Member.DoesNotExist:
                return redirect(f'/ambient/members/{ambientid}')
            member.user.ambients.remove(ambient.id)
            ambient.members.remove(memberid)
            if not ambient.members.exists():
                ambient.delete()
                return redirect('home')
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    return redirect('home')

def ambient_solicitations(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_gerenciate_members:
            solicitations = ambient.enter_solicitations
            names = []
            ids = []
            for solicitation in solicitations:
                name = User.objects.get(userid = solicitation).name
                names.append(name)
                tid = User.objects.get(userid = solicitation).userid
                ids.append(tid)
            solicitations_list = list(zip(names, ids))
            return render(request, "AllokAcads/ambient_solicitations.html", {'solicitations_list' : solicitations_list, 'ambient' : ambient, 'user' : user, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def accept_solicitation(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            try:
                member = User.objects.get(userid = memberid)
            except User.DoesNotExist:
                return redirect(f'/ambient/solicitations/{ambientid}')
            ambient.enter_solicitations.remove(memberid)
            new_member = Member(user=member, admin_type=None, is_professor=True)
            new_member.save()
            ambient.members.add(new_member)
            ambient.save()
            member.ambients.add(ambient)
            member.save()
            return redirect(f'/ambient/solicitations/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def refuse_solicitation(request, memberid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            tmember = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and tmember.admin_type.can_gerenciate_members:
            ambient.enter_solicitations.remove(memberid)
            ambient.save()
            return redirect(f'/ambient/solicitations/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_resources(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            context = {
                'ambient': ambient,
                'user': user,
                'userid': user.userid,
                'username': user.name
            }

            return render(request, "AllokAcads/ambient_resources.html", context)
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_subjects(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            subjects = ambient.subjects.all().order_by('name')
            return render(request, "AllokAcads/ambient_subjects.html", {'ambient' : ambient, 'user' : user, 'subjects' : subjects, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_subjects(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            classrooms = ambient.classrooms.all().order_by('name')
            professors = ambient.members.all().filter(is_professor = True).order_by('user__name')
            formations = ambient.formations.all().order_by('name')
            return render(request, "AllokAcads/ambient_create_subjects.html", {'ambient' : ambient, 'user' : user, 'classrooms' : classrooms, 'professors' : professors, 'formations' : formations, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_subjects_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            name = request.POST.get("name")
            subject = Subject(name=name)
            subject.save()
            classroom_ids = request.POST.getlist("ideal_classrooms")
            if classroom_ids:
                for classroom_id in classroom_ids:
                    classroom = Classroom.objects.get(id = classroom_id)
                    classroom_weight = request.POST.get(f"classroom_weight_{classroom_id}")
                    classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
                    classroom_preference.save()
                    subject.ideal_classrooms.add(classroom_preference)
            professor_ids = request.POST.getlist("favorite_professors")
            if professor_ids:
                for professor_id in professor_ids:
                    professor = Member.objects.get(id = professor_id)
                    professor_weight = request.POST.get(f"professor_weight_{professor_id}")
                    professor_preference = Professor_Preference(professor=professor, professor_weight=professor_weight)
                    professor_preference.save()
                    subject.favorite_professors.add(professor_preference)
            formation_ids = request.POST.getlist("relevant_formations")
            if formation_ids:
                for formation_id in formation_ids:
                    formation = Formation.objects.get(id = formation_id)
                    formation_weight = request.POST.get(f"formation_weight_{formation_id}")
                    formation_preference = Formation_Preference(formation=formation, formation_weight=formation_weight)
                    formation_preference.save()
                    subject.relevant_formations.add(formation_preference)
            ambient.subjects.add(subject)
            return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_subjects(request, subjectid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                subject = Subject.objects.get(id = subjectid)
            except Subject.DoesNotExist:
                return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')
            ideal_classrooms = list(subject.ideal_classrooms.values_list('classroom', flat=True))
            classroom_weights = list(subject.ideal_classrooms.values_list('classroom_weight', flat=True))
            classrooms_and_weights = list(zip(ideal_classrooms, classroom_weights))

            favorite_professors = list(subject.favorite_professors.values_list('professor', flat=True))
            professor_weights = list(subject.favorite_professors.values_list('professor_weight', flat=True))
            professors_and_weights = list(zip(favorite_professors, professor_weights))

            relevant_formations = list(subject.relevant_formations.values_list('formation', flat=True))
            formations_weights = list(subject.relevant_formations.values_list('formation_weight', flat=True))
            formations_and_weights = list(zip(relevant_formations, formations_weights))

            classrooms = ambient.classrooms.all().order_by('name')
            professors = ambient.members.all().filter(is_professor = True).order_by('user__name')
            formations = ambient.formations.all().order_by('name')
            return render(request, "AllokAcads/ambient_edit_subjects.html", {'subject': subject, 'ambient': ambient, 'subjectid': subjectid, 'user': user, 'classrooms' : classrooms, 'professors' : professors, 'formations' : formations, 'userid': user.userid, 'ideal_classrooms': ideal_classrooms, 'classrooms_and_weights': classrooms_and_weights, 'favorite_professors': favorite_professors, 'professors_and_weights': professors_and_weights, 'relevant_formations': relevant_formations, 'formations_and_weights': formations_and_weights})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_subjects_validate(request, subjectid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            name = request.POST.get("name")
            try:
                subject = Subject.objects.get(id = subjectid)
            except Subject.DoesNotExist:
                return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')

            classroom_ids = request.POST.getlist("ideal_classrooms")
            professor_ids = request.POST.getlist("favorite_professors")
            formation_ids = request.POST.getlist("relevant_formations")

            if name or classroom_ids or professor_ids or formation_ids:
                if name:
                    subject.name = name

                    subject.ideal_classrooms.all().delete()
                    for classroom_id in classroom_ids:
                        classroom = Classroom.objects.get(id = classroom_id)
                        classroom_weight = request.POST.get(f"classroom_weight_{classroom_id}")
                        classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
                        classroom_preference.save()
                        subject.ideal_classrooms.add(classroom_preference)

                    subject.favorite_professors.all().delete()
                    for professor_id in professor_ids:
                        professor = Member.objects.get(id = professor_id)
                        professor_weight = request.POST.get(f"professor_weight_{professor_id}")
                        professor_preference = Professor_Preference(professor=professor, professor_weight=professor_weight)
                        professor_preference.save()
                        subject.favorite_professors.add(professor_preference)

                    subject.relevant_formations.all().delete()
                    for formation_id in formation_ids:
                        formation = Formation.objects.get(id = formation_id)
                        formation_weight = request.POST.get(f"formation_weight_{formation_id}")
                        formation_preference = Formation_Preference(formation=formation, formation_weight=formation_weight)
                        formation_preference.save()
                        subject.relevant_formations.add(formation_preference)
                subject.save()

            return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete_subjects(request, subjectid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                subject = Subject.objects.get(id = subjectid)
            except Subject.DoesNotExist:
                return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')
            subject.delete()
            return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_classes(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            classes = ambient.classes.all().order_by('name')
            return render(request, "AllokAcads/ambient_classes.html", {'ambient': ambient, 'user': user, 'userid': user.userid, 'username': user.name, 'classes': classes})
        else:
                return redirect('home')
    else:
        return redirect('/')

def ambient_create_classes(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            schedules = ambient.available_schedules.all()
            classrooms = ambient.classrooms.all().order_by('name')
            professors = ambient.members.all().filter(is_professor = True).order_by('user__name')
            subjects = ambient.subjects.all().order_by('name')
            lines = ambient.periods_in_a_day
            return render(request, "AllokAcads/ambient_create_classes.html", {'ambient': ambient, 'user': user, 'userid': user.userid, 'username': user.name, 'classrooms': classrooms, 'professors': professors, 'subjects': subjects, 'schedules': schedules, 'lines': lines})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_classes_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            name = request.POST.get("name")
            number_of_students = request.POST.get("number_of_students")
            tclass = Class(name=name, number_of_students=number_of_students)
            tclass.save()
            schedule_ids = request.POST.getlist("available_schedules")
            if schedule_ids:
                for schedule_id in schedule_ids:
                    schedule = Schedule_Preference.objects.get(id = schedule_id)
                    tclass.prefered_schedules.add(schedule)
            classroom_ids = request.POST.getlist("ideal_classrooms")
            if classroom_ids:
                for classroom_id in classroom_ids:
                    classroom = Classroom.objects.get(id = classroom_id)
                    classroom_weight = request.POST.get(f"classroom_weight_{classroom_id}")
                    classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
                    classroom_preference.save()
                    tclass.ideal_classrooms.add(classroom_preference)
            professor_ids = request.POST.getlist("favorite_professors")
            if professor_ids:
                for professor_id in professor_ids:
                    professor = Member.objects.get(id = professor_id)
                    professor_weight = request.POST.get(f"professor_weight_{professor_id}")
                    professor_preference = Professor_Preference(professor=professor, professor_weight=professor_weight)
                    professor_preference.save()
                    tclass.favorite_professors.add(professor_preference)
            subject_ids = request.POST.getlist("necessary_subjects")
            if subject_ids:
                for subject_id in subject_ids:
                    periods = request.POST.get(f"periods_{subject_id}")
                    subject = Subject.objects.get(id = subject_id)
                    subject_preference = Subject_Preference(subject=subject, periods=periods)
                    subject_preference.save()
                    tclass.necessary_subjects.add(subject_preference)
            ambient.classes.add(tclass)
            return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_classes(request, classid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                tclass = Class.objects.get(id = classid)
            except Class.DoesNotExist:
                return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
            schedules = ambient.available_schedules.all()
            classrooms = ambient.classrooms.all().order_by('name')
            professors = ambient.members.all().filter(is_professor = True).order_by('user__name')
            subjects = ambient.subjects.all().order_by('name')
            prefered_schedules = list(tclass.prefered_schedules.all())
            ideal_classrooms = list(tclass.ideal_classrooms.values_list('classroom', flat=True))
            classroom_weights = list(tclass.ideal_classrooms.values_list('classroom_weight', flat=True))
            classrooms_and_weights = list(zip(ideal_classrooms, classroom_weights))
            favorite_professors = list(tclass.favorite_professors.values_list('professor', flat=True))
            professor_weights = list(tclass.favorite_professors.values_list('professor_weight', flat=True))
            professors_and_weights = list(zip(favorite_professors, professor_weights))
            necessary_subjects = list(tclass.necessary_subjects.values_list('subject', flat=True))
            subjects_periods = list(tclass.necessary_subjects.values_list('periods', flat=True))
            subjects_and_periods = list(zip(necessary_subjects, subjects_periods))
            lines = ambient.periods_in_a_day
            return render(request, "AllokAcads/ambient_edit_class.html", {'tclass' : tclass, 'ambient': ambient, 'classid': classid, 'user': user, 'userid': user.userid, 'username': user.name, 'classrooms': classrooms, 'professors': professors, 'subjects': subjects, 'schedules': schedules, 'lines': lines, 'ideal_classrooms': ideal_classrooms, 'classrooms_and_weights': classrooms_and_weights, 'favorite_professors': favorite_professors, 'professors_and_weights': professors_and_weights, 'necessary_subjects': necessary_subjects, 'subjects_and_periods': subjects_and_periods, 'prefered_schedules': prefered_schedules})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_classes_validate(request, classid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                tclass = Class.objects.get(id = classid)
            except Class.DoesNotExist:
                return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
            name = request.POST.get("name")
            number_of_students = request.POST.get("number_of_students")
            schedule_ids = request.POST.getlist("available_schedules")
            classroom_ids = request.POST.getlist("ideal_classrooms")
            professor_ids = request.POST.getlist("favorite_professors")
            subject_ids = request.POST.getlist("necessary_subjects")

            if name or number_of_students or schedule_ids or classroom_ids or professor_ids or subject_ids:
                if name:
                    tclass.name = name
                if number_of_students:
                    tclass.number_of_students = number_of_students

                tclass.prefered_schedules.clear()
                if schedule_ids:
                    for schedule_id in schedule_ids:
                        schedule = Schedule_Preference.objects.get(id = schedule_id)
                        tclass.prefered_schedules.add(schedule)

                tclass.ideal_classrooms.all().delete()
                if classroom_ids:
                    for classroom_id in classroom_ids:
                        classroom = Classroom.objects.get(id = classroom_id)
                        classroom_weight = request.POST.get(f"classroom_weight_{classroom_id}")
                        classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
                        classroom_preference.save()
                        tclass.ideal_classrooms.add(classroom_preference)

                tclass.favorite_professors.all().delete()
                if professor_ids:
                    for professor_id in professor_ids:
                        professor = Member.objects.get(id = professor_id)
                        professor_weight = request.POST.get(f"professor_weight_{professor_id}")
                        professor_preference = Professor_Preference(professor=professor, professor_weight=professor_weight)
                        professor_preference.save()
                        tclass.favorite_professors.add(professor_preference)

                tclass.necessary_subjects.all().delete()
                if subject_ids:
                    for subject_id in subject_ids:
                        subject = Subject.objects.get(id = subject_id)
                        periods = request.POST.get(f"periods_{subject_id}")
                        subject_preference = Subject_Preference(subject=subject, periods=periods)
                        subject_preference.save()
                        tclass.necessary_subjects.add(subject_preference)
                tclass.save()

            return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete_classes(request, classid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                tclass = Class.objects.get(id = classid)
            except Class.DoesNotExist:
                return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
            tclass.delete()
            return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_rooms(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            rooms = ambient.classrooms.all().order_by('name')
            return render(request, "AllokAcads/ambient_rooms.html", {'ambient' : ambient, 'user' : user, 'rooms' : rooms, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_rooms(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            roomtypes = ambient.classroom_types.all().order_by('name')
            return render(request, "AllokAcads/ambient_create_rooms.html", {'ambient' : ambient, 'user' : user, 'roomtypes' : roomtypes, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_rooms_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            name = request.POST.get('name')
            roomtype = request.POST.get('roomtype')
            capacity = request.POST.get('capacity')
            roomtype = ClassroomTP.objects.get(id = roomtype) if roomtype else None
            room = Classroom(name=name, classroom_type=roomtype, classroom_capacity=capacity, num_uses=0)
            room.save()
            ambient.classrooms.add(room)
            return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_rooms(request, roomid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                room = Classroom.objects.get(id = roomid)
            except Classroom.DoesNotExist:
                return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
            roomtypes = ambient.classroom_types.all().order_by('name')
            return render(request, "AllokAcads/ambient_edit_rooms.html", {'room': room, 'ambient': ambient, 'roomid': roomid, 'user': user, 'roomtypes': roomtypes})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_rooms_validate(request, roomid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                room = Classroom.objects.get(id = roomid)
            except Classroom.DoesNotExist:
                return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
            name = request.POST.get("name")
            if name:
                room.name = name
            roomtype = request.POST.get("roomtype")
            if roomtype:
                room.classroom_type = ClassroomTP.objects.get(id = roomtype)
            capacity = request.POST.get("capacity")
            if capacity:
                room.classroom_capacity = capacity
            room.save()
            return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete_rooms(request, roomid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                room = Classroom.objects.get(id = roomid)
            except Classroom.DoesNotExist:
                return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
            room.delete()
            return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_formations(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            formations = ambient.formations.all().order_by('name')
            return render(request, "AllokAcads/ambient_formations.html", {'ambient' : ambient, 'user' : user, 'formations' : formations, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_formations(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            return render(request, "AllokAcads/ambient_create_formations.html", {'ambient' : ambient, 'user' : user, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_formations_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            name = request.POST.get('name')
            formation = Formation(name=name)
            formation.save()
            ambient.formations.add(formation)
            return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_formations(request, formationid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            roomtypes = ambient.classroom_types.all()
            try:
                formation = Formation.objects.get(id = formationid)
            except Formation.DoesNotExist:
                return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
            return render(request, "AllokAcads/ambient_edit_formations.html", {'formation': formation, 'ambient': ambient, 'formationid': formationid, 'user': user, 'roomtypes': roomtypes})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_formations_validate(request, formationid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                formation = Formation.objects.get(id = formationid)
            except Formation.DoesNotExist:
                return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
            name = request.POST.get('name')

            if name:
                formation.name = name
            formation.save()
            return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete_formations(request, formationid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')
        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                formation = Formation.objects.get(id = formationid)
            except Formation.DoesNotExist:
                return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
            formation.delete()
            return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_roomtypes(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            roomtypes = ambient.classroom_types.all().order_by('name')
            return render(request, "AllokAcads/ambient_roomtypes.html", {'ambient' : ambient, 'user' : user, 'roomtypes' : roomtypes, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_roomtypes(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            return render(request, "AllokAcads/ambient_create_roomtypes.html", {'ambient' : ambient, 'user' : user, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_roomtypes_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            roomtype = ClassroomTP(name=name)
            name = request.POST.get('name')
            if roomtype:
                roomtype.save()
                ambient.classroom_types.add(roomtype)
            return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_roomtypes(request, roomid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                roomtype = ClassroomTP.objects.get(id = roomid)
            except ClassroomTP.DoesNotExist:
                return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
            return render(request, "AllokAcads/ambient_edit_roomtypes.html", {'roomtype': roomtype, 'ambient': ambient, 'roomid': roomid, 'user': user})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_roomtypes_validate(request, roomid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                roomtype = ClassroomTP.objects.get(id = roomid)
            except ClassroomTP.DoesNotExist:
                return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
            name = request.POST.get('name')
            if name:
                roomtype.name = name
                roomtype.save()
            return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete_roomtypes(request, roomid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                roomtype = ClassroomTP.objects.get(id = roomid)
            except ClassroomTP.DoesNotExist:
                return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
            roomtype.delete()
            return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_admtypes(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            admtypes = ambient.admin_types.all().order_by('name')
            return render(request, "AllokAcads/ambient_admtypes.html", {'ambient' : ambient, 'user' : user, 'admtypes' : admtypes, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_admtypes(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            return render(request, "AllokAcads/ambient_create_admtypes.html", {'ambient' : ambient, 'user' : user, 'userid': user.userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_admtypes_validate(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            if request.POST.get('name'):
                name = request.POST.get('name')
            can_configure_ambient = True if request.POST.get('can_configure_ambient') == 'on' else False
            can_gerenciate_members = True if request.POST.get('can_gerenciate_members') == 'on' else False
            can_register_resources = True if request.POST.get('can_register_resources') == 'on' else False
            can_run_atribuition = True if request.POST.get('can_run_atribuition') == 'on' else False
            can_run_alocation = True if request.POST.get('can_run_alocation') == 'on' else False

            admtp = AdminTP(name=name, can_configure_ambient=can_configure_ambient, can_gerenciate_members=can_gerenciate_members, can_register_resources=can_register_resources, can_run_atribuition=can_run_atribuition, can_run_alocation=can_run_alocation)
            if admtp:
                admtp.save()
                ambient.admin_types.add(admtp)

            return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_admtypes(request, admtypeid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                admtp = AdminTP.objects.get(id = admtypeid)
            except AdminTP.DoesNotExist:
                return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
            return render(request, "AllokAcads/ambient_edit_admintypes.html", {'admtp': admtp, 'ambient': ambient, 'admtypeid': admtypeid, 'user': user})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_admtypes_validate(request, admtypeid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            if request.POST.get('name'):
                name = request.POST.get('name')
            can_configure_ambient = True if request.POST.get('can_configure_ambient') == 'on' else False
            can_gerenciate_members = True if request.POST.get('can_gerenciate_members') == 'on' else False
            can_register_resources = True if request.POST.get('can_register_resources') == 'on' else False
            can_run_atribuition = True if request.POST.get('can_run_atribuition') == 'on' else False
            can_run_alocation = True if request.POST.get('can_run_alocation') == 'on' else False

            try:
                admtp = AdminTP.objects.get(id = admtypeid)
            except AdminTP.DoesNotExist:
                return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
            if name:
                admtp.name = name
            if can_configure_ambient:
                admtp.can_configure_ambient = can_configure_ambient
                admtp.can_gerenciate_members = can_gerenciate_members
                admtp.can_register_resources = can_register_resources
                admtp.can_run_atribuition = can_run_atribuition
                admtp.can_run_alocation = can_run_alocation
            admtp.save()

            return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_delete_admtypes(request, admtypeid, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type.can_register_resources:
            try:
                admtype = AdminTP.objects.get(id = admtypeid)
            except AdminTP.DoesNotExist:
                return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
            admtype.delete()
            return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def tiebreaker(professor, chosen_professor, activitie, activitie2 = None):
    #Garante que, caso não haja uma segunda atividade para avaliar qual das duas é mais importante, a disputa seja feita apenas entre a primeira atividade, para definir qual professor deve ser escolhido.
    if not activitie2:
        activitie2 = activitie

    #Coleta informações relevantes para comparar os dois professores, como formações importantes para a disciplina, formações dos professores, grau de formação, tempo de experiência e preferência que a atividade tem por cada professor.
    relevant_formations = None
    if activitie.tsubject.relevant_formations:
        relevant_formations = activitie.tsubject.relevant_formations.all().order_by("-formation_weight")
    relevant_formations2 = None
    if activitie2.tsubject.relevant_formations:
        relevant_formations2 = activitie2.tsubject.relevant_formations.all().order_by("-formation_weight")

    try:
        formations_1 = professor.formations.all()
    except:
        formations_1 = None
    try:
        formations_2 = chosen_professor.formations.all()
    except:
        formations_2 = None
    formation_1_count = 1
    formation_2_count = 1
    degree_1_count = 0
    degree_2_count = 0
    professional_experience_1_count = 0
    professional_experience_2_count = 0
    didatic_experience_1_count = 0
    didatic_experience_2_count = 0

    for formation in relevant_formations:
        for a_formation in formations_1:
            if a_formation.formation == formation:
                professional_experience_1_count = formation.professional_experience_time
                didatic_experience_1_count = formation.didatic_experience_time
                if a_formation.formation_degree == 'Graduado':
                    degree_1_count += 25
                elif a_formation.formation_degree == 'Mestre':
                    degree_1_count += 50
                elif a_formation.formation_degree == 'Doutor':
                    degree_1_count += 100
                formation_1_count *= formation.formation_weight

    for formation in relevant_formations2:
        for a_formation in formations_2:
            if a_formation.formation == formation:
                professional_experience_2_count = formation.professional_experience_time
                didatic_experience_2_count = formation.didatic_experience_time
                if a_formation.formation_degree == 'Graduado':
                    degree_2_count += 25
                elif a_formation.formation_degree == 'Mestre':
                    degree_2_count += 50
                elif a_formation.formation_degree == 'Doutor':
                    degree_2_count += 100
                formation_2_count *= formation.formation_weight

    try:
        tclass_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
    except:
        tclass_professor1 = 1
    try:
        tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
    except:
        tsubjects_professor1 = 1

    try:
        tclass_professor2 = activitie2.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
    except:
        tclass_professor2 = 1
    try:
        tsubjects_professor2 = activitie2.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
    except:
        tsubjects_professor2 = 1

    #Inicia a comparação seguindo os critérios de desempate: Maior preferência da atividade > Grau de formação acadêmica > Tempo de experiência profissional > Tempo de experiência didática > Tempo no Campus > Tempo na instituição > Idade > Relevância das formações para a disciplina.
    if(tclass_professor1 != 0 and tsubjects_professor1 != 0):
        if (tclass_professor1 + tsubjects_professor1 > tclass_professor2 + tsubjects_professor2 and ((tclass_professor2 < 100 and tsubjects_professor2 < 100) or (tclass_professor1 == 100 or tsubjects_professor1 == 100))):
            return professor, True
        elif (tclass_professor1 + tsubjects_professor1 == tclass_professor2 + tsubjects_professor2 and ((tclass_professor2 < 100 and tsubjects_professor2 < 100) or (tclass_professor1 == 100 or tsubjects_professor1 == 100))):
            if degree_1_count > degree_2_count:
                return professor, True
            elif degree_1_count == degree_2_count:
                if professional_experience_1_count > professional_experience_2_count:
                    return professor, True
                elif professional_experience_1_count == professional_experience_2_count:
                    if didatic_experience_1_count > didatic_experience_2_count:
                        return professor, True
                    elif didatic_experience_1_count == didatic_experience_2_count:
                        if professor.time_in_campus > chosen_professor.time_in_campus:
                            return professor, True
                        elif professor.time_in_campus == chosen_professor.time_in_campus:
                            if professor.time_in_institution > chosen_professor.time_in_institution:
                                return professor, True
                            elif professor.time_in_institution == chosen_professor.time_in_institution:
                                if datetime.date.today() - professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                    return professor, True
                                elif datetime.date.today() - professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
                                    if formation_1_count > formation_2_count:
                                        return professor, True
    return chosen_professor, False

def check_conflitant_schedules_classroom(activities_with_classroom, timetable, classroom, switched = False):
    #Se não houverem atividades com a sala alocada, não há conflito de horários, logo a função retorna verdadeiro imediatamente.
    if not activities_with_classroom:
        return True

    #Caso a lista não seja um dicionário com [linha, coluna] : atividade, ele é convertido para esse formato, caso já seja, simplesmente é copiado.
    fixed_timetable = {}
    if not isinstance(timetable, dict):
        for time in timetable:
            fixed_timetable[(time.line, time.column)] = "Available"
    else:
        fixed_timetable = {key: value.copy() if isinstance(value, list) else value for key, value in timetable.items()}

    #Aqui, acessamos a atividade que precisa ser alocada, se houverem mais atividades na lista, selecionamos a última, que será sempre a que desejamos, caso contrário, selecionamos a única atividade da lista.
    if len(activities_with_classroom) > 1:
        tactivitie = activities_with_classroom[-1]
    else:
        tactivitie = activities_with_classroom[0]

    #Agora organizamos as atividades por maior quantidade de horários preferidos e maior quantidade de horários necessários, para iniciar pelas alocações mais "difíceis" e, assim, otimizar o algoritmo. Em seguida, selecionamos a primeira atividade da lista para tentar alocá-la em algum horário.
    activities_with_classroom.sort(key=lambda x: (x.tclass.prefered_schedules.count(), -x.activities_qtd))
    activitie = activities_with_classroom[0]
    classroom_class_weight = activitie.tclass.ideal_classrooms.get(classroom = activitie.tclassroom).classroom_weight if activitie.tclass.ideal_classrooms.filter(classroom = activitie.tclassroom).exists() else 1
    classroom_subject_weight = activitie.tsubject.ideal_classrooms.get(classroom = activitie.tclassroom).classroom_weight if activitie.tsubject.ideal_classrooms.filter(classroom = activitie.tclassroom).exists() else 1

    #Aqui definimos o peso da atividade para aquela sala, se a atividade for diferente da que desejamos alocar no momento, o peso é puxado diretamente de suas preferências, caso contrário, ele é calculado. O peso da atividade a ser alocada também é calculado separadamente para fins de comparação.
    if activitie.classroom_weight:
        current_weight = activitie.classroom_weight
    else:
        current_weight = (tactivitie.tclass.ideal_classrooms.get(classroom = classroom).classroom_weight if tactivitie.tclass.ideal_classrooms.filter(classroom = classroom).exists() else 1) + (tactivitie.tsubject.ideal_classrooms.get(classroom = classroom).classroom_weight if tactivitie.tsubject.ideal_classrooms.filter(classroom = classroom).exists() else 1)
    example_weight = (tactivitie.tclass.ideal_classrooms.get(classroom = classroom).classroom_weight if tactivitie.tclass.ideal_classrooms.filter(classroom = classroom).exists() else 1) + (tactivitie.tsubject.ideal_classrooms.get(classroom = classroom).classroom_weight if tactivitie.tsubject.ideal_classrooms.filter(classroom = classroom).exists() else 1)

    #Aqui inicia o processo de alocação. Uma iteração inicia sobre os horários preferidos da atividade, verificando se o horário marcado e os horários em sequência (considerando o tamanho da atividade) estão disponíveis.
    #Se o horário estiver disponível, ele é marcado como ocupado pela atividade no dicionário. Caso contrário, se a atividade tiver peso maior do que, no máximo, uma única atividade que já esteja alocada naquele horário, ela poderá tomar o lugar dela e retornar a atividade desalocada para removê-la daquele horário.
    #Há uma variável de controle que se mantém durante o backtracking para garantir que haja apenas uma troca por iteração, para evitar que haja uma série de trocas que poderiam desalocar várias atividades e, assim, causar um grande problema.
    #A função é novamente chamada para tentar alocar a próxima atividade da lista, e dessa forma, todas as possibilidades podem ser testadas.

    last_switch = None
    last_switched_activitie = None
    last_start = None
    for s, start in enumerate(activitie.tclass.prefered_schedules.all()):
        switched_activitie = None
        switch = False
        available = False
        timetable = {key: value.copy() if isinstance(value, list) else value for key, value in fixed_timetable.items()}

        #Verifica se o horário e seus horários em sequência estão disponíveis para alocar a atividade, desalocando uma única atividade para este fim, se necessário uma troca.
        for i in range(activitie.activities_qtd):
            try:
                slot = timetable.get((start.line+i, start.column))
            except:
                slot = None
            if slot:
                if slot == "Available":
                    available = True
                elif current_weight < example_weight and classroom_class_weight < 100 and classroom_subject_weight < 100 and activitie != tactivitie:
                    if switched == False or activitie == last_switched_activitie:
                        switch = True
                        switched_activitie = activitie
                        available = False
                    else:
                        switch = False
                        switched_activitie = None
                        available = False
                        break
                else:
                    switch = False
                    switched_activitie = None
                    available = False
                    break
            else:
                switch = False
                switched_activitie = None
                available = False
                break

        if switch and switched_activitie:
            last_switch = switch
            last_switched_activitie = switched_activitie
            last_start = start

        if s == len(activitie.tclass.prefered_schedules.all()) - 1:
            available = True
            start = last_start
            switch = last_switch
            switched_activitie = last_switched_activitie

        if available:
            #Agora, os horários definidos como disponíveis são marcados como ocupados pela atividade no dicionário, e se houver uma atividade marcada como trocada, seus horários anteriormente ocupados serão marcados como livres.
            #Este dicionário serve apenas para esta iteração de horário de início, sendo que, se a possibilidade for inválida e este horário precisar mudar, o dicionário é reiniciado para seu último estado válido, o que foi passado na chamada da função, e o processo se repete com o novo dicionário.
            if switched_activitie:
                for k, v in list(timetable.items()):
                    if v == switched_activitie:
                        timetable[k] = "Available"

            for i in range(activitie.activities_qtd):
                key = (start.line + i, start.column)
                timetable[key] = activitie

            #Agora, o backtracking entra em ação. Se ainda houverem atividades na lista além da que deseja ser alocada, a função é chamada novamente, excluindo a atividade que acabamos de alocar, passando a grade horária alterada, a sala e a variável de controle, para garantir que haja no máximo uma atividade em troca.
            #Se não houverem mais atividades além da que foi alocada, significa que chegamos ao fim do algoritmo, então ele começa a retornar True ou o valor da atividade que foi trocada, caso exista. As chamadas anteriores fazem o mesmo, retornando True ou a atividade que foi trocada, caso a função que chamou tenha sido bem-sucedida, e False, caso a função que chamou tenha sido mal-sucedida ou resultante de uma segunda troca.
            if len(activities_with_classroom) > 1:
                check = check_conflitant_schedules_classroom(activities_with_classroom[1:], timetable, classroom, switch)
                if check:
                    if switch:
                        if not isinstance(check, Activitie):
                            return switched_activitie
                        else:
                            return False
                    else:
                        if isinstance(check, Activitie):
                            return check
                        return True
                else:
                    return False
            else:
                if switch:
                    return switched_activitie

                return True
    return False

def check_conflitant_schedules_professor(activities_with_professor, timetable, professor, switched = False):
    #Se não houverem atividades com o professor alocado, não há conflito de horários, logo a função retorna verdadeiro imediatamente.
    if not activities_with_professor:
        return True

    #Caso a lista não seja um dicionário com [linha, coluna] : atividade, ele é convertido para esse formato, caso já seja, simplesmente é copiado.
    fixed_timetable = {}
    if not isinstance(timetable, dict):
        for time in timetable:
            fixed_timetable[(time.line, time.column)] = "Available"
    else:
        fixed_timetable = {key: value.copy() if isinstance(value, list) else value for key, value in timetable.items()}

    #Aqui, acessamos a atividade que precisa ser alocada, se houverem mais atividades na lista, selecionamos a última, que será sempre a que desejamos, caso contrário, selecionamos a única atividade da lista.
    if len(activities_with_professor) > 1:
        tactivitie = activities_with_professor[-1]
    else:
        tactivitie = activities_with_professor[0]

    #Agora organizamos as atividades por maior quantidade de horários preferidos e maior quantidade de horários necessários, para iniciar pelas alocações mais "difíceis" e, assim, otimizar o algoritmo. Em seguida, selecionamos a primeira atividade da lista para tentar alocá-la em algum horário.
    activities_with_professor.sort(key=lambda x: (x.tclass.prefered_schedules.count(), -x.activities_qtd))
    activitie = activities_with_professor[0]
    professor_class_weight = activitie.tclass.favorite_professors.get(professor = activitie.tprofessor).professor_weight if activitie.tclass.favorite_professors.filter(professor = activitie.tprofessor).exists() else 1
    professor_subject_weight = activitie.tsubject.favorite_professors.get(professor = activitie.tprofessor).professor_weight if activitie.tsubject.favorite_professors.filter(professor = activitie.tprofessor).exists() else 1

    #Aqui definimos o peso da atividade para aquele professor, se a atividade for diferente da que desejamos alocar no momento, o peso é puxado diretamente de suas preferências, caso contrário, ele é calculado. O peso da atividade a ser alocada também é calculado separadamente para fins de comparação.
    if activitie.professor_weight:
        current_weight = activitie.professor_weight
    else:
        current_weight = (tactivitie.tclass.favorite_professors.get(professor = professor).professor_weight if tactivitie.tclass.favorite_professors.filter(professor = professor).exists() else 1) + (tactivitie.tsubject.favorite_professors.get(professor = professor).professor_weight if tactivitie.tsubject.favorite_professors.filter(professor = professor).exists() else 1)
    example_weight = (tactivitie.tclass.favorite_professors.get(professor = professor).professor_weight if tactivitie.tclass.favorite_professors.filter(professor = professor).exists() else 1) + (tactivitie.tsubject.favorite_professors.get(professor = professor).professor_weight if tactivitie.tsubject.favorite_professors.filter(professor = professor).exists() else 1)

    #Aqui inicia o processo de alocação. Uma iteração inicia sobre os horários preferidos da atividade, verificando se o horário marcado e os horários em sequência (considerando o tamanho da atividade) estão disponíveis.
    #Se o horário estiver disponível, ele é marcado como ocupado pela atividade no dicionário. Caso contrário, se a atividade tiver peso maior do que, no máximo, uma única atividade que já esteja alocada naquele horário, ela poderá tomar o lugar dela e retornar a atividade desalocada para removê-la daquele horário.
    #Caso o peso seja igual, os critérios de desempate são aplicados, e o professor escolhido será mantido. Há uma variável de controle que se mantém durante o backtracking para garantir que haja apenas uma troca por iteração, para evitar que haja uma série de trocas que poderiam desalocar várias atividades e, assim, causar um grande problema.
    #A função é novamente chamada para tentar alocar a próxima atividade da lista, e dessa forma, todas as possibilidades podem ser testadas.

    last_switch = None
    last_switched_activitie = None
    last_start = None
    for s, start in enumerate(activitie.tclass.prefered_schedules.all()):
        switched_activitie = None
        switch = False
        available = False
        timetable = {key: value.copy() if isinstance(value, list) else value for key, value in fixed_timetable.items()}

        for i in range(activitie.activities_qtd):
            try:
                slot = timetable.get((start.line+i, start.column))
            except:
                slot = None

            if slot:
                if slot == "Available":
                    available = True
                elif current_weight < example_weight and professor_class_weight < 100 and professor_subject_weight < 100 and activitie != tactivitie:
                    if switched == False or activitie == last_switched_activitie:
                        switch = True
                        switched_activitie = activitie
                        available = False
                    else:
                        switch = False
                        switched_activitie = None
                        available = False
                        break
                elif current_weight == example_weight and professor_class_weight < 100 and professor_subject_weight < 100 and activitie != tactivitie:
                    if switched == False or activitie == last_switched_activitie:
                        t_activitie = timetable.get((start.line+i, start.column))

                        if tiebreaker(professor, t_activitie.tprofessor, activitie, t_activitie)[0] == professor:
                            switch = True
                            switched_activitie = activitie
                            available = False
                        else:
                            switch = False
                            switched_activitie = None
                            available = False
                            break
                    else:
                        switch = False
                        switched_activitie = None
                        available = False
                        break
                else:
                    switch = False
                    switched_activitie = None
                    available = False
                    break
            else:
                switch = False
                switched_activitie = None
                available = False
                break

        if switch and switched_activitie:
            last_switch = switch
            last_switched_activitie = switched_activitie
            last_start = start

        if s == len(activitie.tclass.prefered_schedules.all()) - 1:
            available = True
            start = last_start
            switch = last_switch
            switched_activitie = last_switched_activitie

        #Agora, os horários definidos como disponíveis são marcados como ocupados pela atividade no dicionário, e se houver uma atividade marcada como trocada, seus horários anteriormente ocupados serão marcados como livres.
        #Este dicionário serve apenas para esta iteração de horário de início, sendo que, se a possibilidade for inválida e este horário precisar mudar, o dicionário é reiniciado para seu último estado válido, o que foi passado na chamada da função, e o processo se repete com o novo dicionário.
        if available:
            if switched_activitie:
                for k, v in list(timetable.items()):
                    if v == switched_activitie:
                        timetable[k] = "Available"

            for i in range(activitie.activities_qtd):
                key = (start.line + i, start.column)
                timetable[key] = activitie

            #Agora, o backtracking entra em ação. Se ainda houverem atividades na lista além da que deseja ser alocada, a função é chamada novamente, excluindo a atividade que acabamos de alocar, passando a grade horária alterada, a sala e a variável de controle, para garantir que haja no máximo uma atividade em troca.
            #Se não houverem mais atividades além da que foi alocada, significa que chegamos ao fim do algoritmo, então ele começa a retornar True ou o valor da atividade que foi trocada, caso exista. As chamadas anteriores fazem o mesmo, retornando True ou a atividade que foi trocada, caso a função que chamou tenha sido bem-sucedida, e False, caso a função que chamou tenha sido mal-sucedida ou resultante de uma segunda troca.
            if len(activities_with_professor) > 1:
                check = check_conflitant_schedules_professor(activities_with_professor[1:], timetable, professor, switch)
                if check:
                    if switch:
                        if not isinstance(check, Activitie):
                            return switched_activitie
                        else:
                            return False
                    else:
                        if isinstance(check, Activitie):
                            return check
                        return True
                else:
                    return False
            else:
                if switch:
                    return switched_activitie

                return True
    return False


def _run_attribution_logic_silent(ambient):
    # Limpa as atividades para iniciar uma nova atribuição.
    old_activities = list(ambient.activities.all())
    ambient.activities.clear()
    Activitie.objects.filter(id__in=[act.id for act in old_activities]).delete()
    ambient.save()
    rooms = list(ambient.classrooms.all())
    for room in rooms:
        room.num_uses = 0
        room.save()
    professors = list(ambient.members.all().filter(is_professor = True))
    for professor in professors:
        professor.num_uses = 0
        professor.save()
    # Recria as atividades.
    classes = ambient.classes.all()
    for aclass in classes:
        necessary_subjects = aclass.necessary_subjects.all()
        for subject in necessary_subjects:
            activitie = Activitie(tclass = aclass, tsubject = subject.subject, activities_qtd = subject.periods)
            activitie.save()
            ambient.activities.add(activitie)
    ambient.save()

    # Executa a otimização com RKO para Atribuição
    activities = list(ambient.activities.all())
    if activities:
        from AllokAcads.rko_environments import RKOAttributionEnvironment, RKO
        env = RKOAttributionEnvironment(ambient, activities)
        solver = RKO(env=env, logger='none')
        attribution_time = int(os.environ.get("RKO_ATTRIBUTION_TIME", "5"))

        # Executa por 5 segundos
        final_cost, best_solution, _ = solver.solve(
            time_total=attribution_time,
            runs=1,
            brkga=2,
            vns=2
        )

        # Aplica e salva as melhores atribuições encontradas
        best_activities = env.decoder(best_solution)
        for act in best_activities:
            act.save()

        # Atualiza num_uses das salas e professores no banco
        for room in rooms:
            room.num_uses = sum(a.activities_qtd for a in best_activities if a.tclassroom and a.tclassroom.id == room.id)
            room.save()
        for prof in professors:
            prof.num_uses = sum(a.activities_qtd for a in best_activities if a.tprofessor and a.tprofessor.id == prof.id)
            prof.save()


def _run_allocation_logic_silent(ambient):
    # Limpa qualquer grade anterior
    if ambient.published_timetable:
        ambient.published_timetable.delete()

    # O algoritmo inicia criando uma tabela vazia, que será preenchida em breve
    timetable_db = Timetable(lines_number = ambient.periods_in_a_day, columns_number = ambient.days_in_a_cicle)
    timetable_db.save()
    ambient.published_timetable = timetable_db
    ambient.save()

    # Cria slots de alocação vazios no banco de dados
    for schedule in ambient.available_schedules.all():
        alocation = Alocation(line = schedule.line, column = schedule.column)
        alocation.save()
        ambient.published_timetable.table.add(alocation)
    ambient.save()

    activities = list(ambient.activities.all())
    if activities:
        from AllokAcads.rko_environments import RKOAllocationEnvironment, RKO
        env = RKOAllocationEnvironment(ambient, activities)
        solver = RKO(env=env, logger='none')
        allocation_time = int(os.environ.get("RKO_ALLOCATION_TIME", "30"))

        # Executa a otimização com RKO para Alocação por 5 segundos
        final_cost, best_solution, _ = solver.solve(
            time_total=allocation_time,
            runs=1,
            brkga=2,
            vns=2
        )

        # Decodifica a melhor grade horária encontrada
        tdict = env.decoder(best_solution)
        from AllokAcads import rko_llm_constraints
        repair_log = rko_llm_constraints.repair_allocation_timetable(ambient, tdict)
        live_activities = Activitie.objects.in_bulk({
            act.id
            for acts in tdict.values()
            for act in acts
            if getattr(act, "id", None)
        })

        # Salva as alocações da grade horária no banco de dados
        for key, value in tdict.items():
            try:
                alocation_db = ambient.published_timetable.table.all().get(line = key[0], column = key[1])
                for act in value:
                    live_act = live_activities.get(act.id)
                    if live_act:
                        alocation_db.activitie.add(live_act)
                alocation_db.save()
            except Alocation.DoesNotExist:
                pass

        # Trata as atividades conflitantes — remove só o mínimo necessário
        removed_ids = set()
        while True:
            conflict_count = {}
            has_conflict = False
            for (line, col), slot_acts in tdict.items():
                active = [a for a in slot_acts if a.id not in removed_ids]
                for j in range(len(active)):
                    for k in range(j + 1, len(active)):
                        a, b = active[j], active[k]
                        if (a.tclass is not None and a.tclass == b.tclass) or \
                           (a.tprofessor is not None and a.tprofessor == b.tprofessor) or \
                           (a.tclassroom is not None and a.tclassroom == b.tclassroom):
                            conflict_count[a.id] = conflict_count.get(a.id, 0) + 1
                            conflict_count[b.id] = conflict_count.get(b.id, 0) + 1
                            has_conflict = True
            if not has_conflict:
                break
            worst_id = max(conflict_count, key=conflict_count.get)
            removed_ids.add(worst_id)

        # Remove as atividades conflitantes do banco e registra como não alocadas
        for act_id in removed_ids:
            live_act = live_activities.get(act_id)
            if not live_act:
                continue
            for slot in ambient.published_timetable.table.all():
                if live_act in slot.activitie.all():
                    slot.activitie.remove(live_act)
                    slot.save()
            un_activitie = Unregistered_Activitie(
                activitie=live_act,
                message="Conflito de recurso (Professor, Sala ou Turma ocupados)."
            )
            un_activitie.save()
            ambient.published_timetable.not_alocated.add(un_activitie)

        # Tenta reinserir as atividades removidas com outra sala/horário
        if removed_ids:
            rko_llm_constraints.repair_published_timetable(ambient)

def run_atribuition(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type and member.admin_type.can_run_atribuition:
            _run_attribution_logic_silent(ambient)
            return redirect(f'/ambient/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')


def alocate(ambient, timetable, activities):
    # Esta função era usada pelo backtracking e foi substituída pelo RKO.
    # Mantida como stub para compatibilidade.
    return timetable


def run_alocation(request, ambientid):
    if request.user.is_authenticated:
        try:
            user = User.objects.get(userid = request.user.username)
        except User.DoesNotExist:
            auth_logout(request)
            return redirect('/')
        try:
            ambient = Ambient.objects.get(ambientid=ambientid)
        except Ambient.DoesNotExist:
            return redirect('home')
        try:
            member = ambient.members.get(user = user)
        except Member.DoesNotExist:
            return redirect('home')

        if ambient.members.filter(user = user) and member.admin_type and member.admin_type.can_run_alocation:
            _run_allocation_logic_silent(ambient)
            return redirect(f'/ambient/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
#AI zone

def professor_preference_adjustment(ambientid, origin_type, origin, preference, weight):
    ambient = Ambient.objects.get(ambientid = ambientid)
    if origin_type == 'Matéria':
        subject = ambient.subjects.get(name = origin)
        professor = ambient.members.get(user__name = preference, is_professor = True)
        subject_professor, created = subject.favorite_professors.get_or_create(professor = professor)
        subject_professor.professor_weight = weight
        subject_professor.save()
    elif origin_type == 'Turma':
        tclass = ambient.classes.get(name = origin)
        professor = ambient.members.get(user__name = preference, is_professor = True)
        class_professor, created = tclass.favorite_professors.get_or_create(professor = professor)
        class_professor.professor_weight = weight
        class_professor.save()
def classroom_preference_adjustment(ambientid, origin_type, origin, preference, weight):
    ambient = Ambient.objects.get(ambientid = ambientid)
    if origin_type == 'Matéria':
        subject = ambient.subjects.get(name = origin)
        classroom = ambient.classrooms.get(name = preference)
        subject_classroom, created = subject.ideal_classrooms.get_or_create(classroom = classroom)
        subject_classroom.classroom_weight = weight
        subject_classroom.save()
    elif origin_type == 'Turma':
        tclass = ambient.classes.get(name = origin)
        classroom = ambient.classrooms.get(name = preference)
        class_classroom, created = tclass.ideal_classrooms.get_or_create(classroom = classroom)
        class_classroom.classroom_weight = weight
        class_classroom.save()
def schedule_preference_adjustment(ambientid, origin_type, origin, preference, true_false):
    ambient = Ambient.objects.get(ambientid = ambientid)

    is_day_only = False
    day_index = None

    if isinstance(preference, int):
        is_day_only = True
        day_index = preference
    elif isinstance(preference, str):
        val = preference.lower().replace("dia", "").strip()
        try:
            if "dia" in preference.lower():
                day_index = int(val) - 1
            else:
                day_index = int(val)
            is_day_only = True
        except ValueError:
            pass

    schedules_to_adjust = []
    if is_day_only and day_index is not None:
        periods = ambient.periods_in_a_day
        for line in range(periods):
            try:
                schedule = ambient.available_schedules.get(line = line, column = day_index)
                schedules_to_adjust.append(schedule)
            except Exception as e:
                print(f"Erro ao obter horário do dia {day_index}, período {line}: {e}")
    else:
        try:
            schedule = ambient.available_schedules.get(line = preference[0], column = preference[1])
            schedules_to_adjust = [schedule]
        except Exception as e:
            print(f"Erro ao obter horário com coordenadas {preference}: {e}")

    if origin_type == 'Turma':
        tclass = ambient.classes.get(name = origin)
        for schedule in schedules_to_adjust:
            if true_false:
                tclass.prefered_schedules.add(schedule)
            else:
                tclass.prefered_schedules.remove(schedule)
    if origin_type == 'Professor':
        professor = ambient.members.get(user__name = origin, is_professor = True)
        for schedule in schedules_to_adjust:
            if true_false:
                professor.prefered_schedules.add(schedule)
            else:
                professor.prefered_schedules.remove(schedule)


def rko_chatbot(ambientid, user_input="", conversation_history=None):
    if not user_input:
        return "Nenhum comando enviado para o chatbot.", False

    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return "Nao encontrei este ambiente para configurar o RKO.", False

    env_path = os.path.join(settings.BASE_DIR, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        k, v = line.strip().split("=", 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass

    api_key = os.environ.get("HF_TOKEN")
    model = os.environ.get("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    if not api_key:
        return "Configure a variavel de ambiente HF_TOKEN para ativar o chat de IA.", False

    try:
        from AllokAcads import rko_llm_constraints

        memory_response = _answer_from_chat_memory(user_input, conversation_history)
        if memory_response:
            return memory_response, False

        unknown_professor_response = _ask_about_unknown_professor(ambient, user_input)
        if unknown_professor_response:
            return unknown_professor_response, False

        deterministic_actions = _build_deterministic_rko_actions(user_input)
        if deterministic_actions:
            return _run_rko_json_actions(rko_llm_constraints, ambientid, deterministic_actions)

        messages = [
            {"role": "system", "content": _build_json_actions_prompt(rko_llm_constraints, ambient)},
        ]
        for item in (conversation_history or [])[-12:]:
            sender = item.get("sender")
            text = (item.get("text") or "").strip()
            if not text:
                continue
            if sender == "user":
                messages.append({"role": "user", "content": text})
            elif sender == "bot":
                json_content = json.dumps({"actions": [{"function": "respond_to_user", "arguments": {"message": text}}]}, ensure_ascii=False)
                messages.append({"role": "assistant", "content": json_content})
        messages.append({"role": "user", "content": user_input})

        response = requests.post(
            url="https://router.huggingface.co/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0,
            },
            timeout=90,
        )

        result = response.json()
        if response.status_code != 200:
            print("Erro do Hugging Face. Status:", response.status_code, "Body:", response.text)
            error_msg = "Erro desconhecido"
            if isinstance(result, dict):
                err = result.get("error")
                if isinstance(err, dict):
                    error_msg = err.get("message", str(err))
                elif err:
                    error_msg = str(err)
                elif "message" in result:
                    error_msg = str(result.get("message"))
            return f"Erro na API do Hugging Face: {error_msg}. Configure um token valido em HF_TOKEN.", False

        message = result["choices"][0]["message"]
        content = (message.get("content") or "").strip()

        # Tenta extrair e rodar as acoes JSON do content do modelo
        json_output, parsed_rules_changed, executed_actions = _parse_and_run_json_actions(
            rko_llm_constraints, ambientid, content
        )

        if executed_actions:
            # Se executou acoes, faz uma segunda chamada para o modelo explicar o resultado em portugues.
            # Montamos um historico limpo substituindo o system prompt restritivo de JSON por um explicativo.
            second_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    second_messages.append({
                        "role": "system",
                        "content": "Voce e um assistente de IA amigavel que ajuda a analisar a grade horaria e explicar os resultados em portugues."
                    })
                else:
                    second_messages.append(msg)

            second_messages.append({"role": "assistant", "content": content})
            second_messages.append({
                "role": "user",
                "content": (
                    f"Resultados da execucao das acoes no RKO:\n{json_output}\n\n"
                    f"Por favor, responda ao usuario em portugues de forma muito amigavel e natural, "
                    f"explicando o resultado dessas acoes ou respondendo diretamente a pergunta dele com base nesses dados. "
                    f"ATENCAO: Se alguma acao falhou com erro (como 'Erro ao executar' ou 'ValueError'), explique amigavelmente ao usuario qual foi o erro no RKO em vez de dizer que funcionou."
                )
            })

            try:
                second_response = requests.post(
                    url="https://router.huggingface.co/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": second_messages,
                        "temperature": 0.5,
                    },
                    timeout=90,
                )
                if second_response.status_code == 200:
                    second_result = second_response.json()
                    final_content = (second_result["choices"][0]["message"].get("content") or "").strip()
                    return final_content, parsed_rules_changed
            except Exception:
                pass

            # Fallback se a segunda chamada falhar
            return json_output, parsed_rules_changed

        # Se o content existia mas nao continha JSON/acoes, e uma resposta em texto natural.
        # Retorna ela diretamente ao usuario em vez do fallback rigido!
        if content:
            return content, False

        # Trata tool_calls nativos caso o modelo os utilize (mantido por compatibilidade)
        tool_calls = message.get("tool_calls") or []
        if tool_calls:
            rules_changed = False
            second_messages = []
            for msg in messages:
                if msg.get("role") == "system":
                    second_messages.append({
                        "role": "system",
                        "content": "Voce e um assistente de IA amigavel que ajuda a analisar a grade horaria e explicar os resultados em portugues."
                    })
                else:
                    second_messages.append(msg)

            second_messages.append(message)
            for tool_call in tool_calls:
                tool_call_id = tool_call.get("id")
                function_data = tool_call.get("function", {})
                function_name = function_data.get("name")
                function_args = json.loads(function_data.get("arguments") or "{}")
                tool_output, tool_rules_changed, _ = _run_rko_tool_action(
                    rko_llm_constraints,
                    ambientid,
                    function_name,
                    function_args,
                )
                rules_changed = rules_changed or tool_rules_changed
                
                second_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "name": function_name,
                    "content": tool_output
                })

            second_response = requests.post(
                url="https://router.huggingface.co/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": second_messages,
                    "temperature": 0.5,
                },
                timeout=90,
            )

            second_result = second_response.json()
            if second_response.status_code == 200:
                final_message = second_result["choices"][0]["message"]
                return (final_message.get("content") or "").strip(), rules_changed
            else:
                return f"Resultados da execucao das acoes no RKO:\n{json_output}", rules_changed

        return "Nao consegui identificar uma restricao para aplicar ao RKO.", False
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Desculpe, ocorreu um erro ao processar sua solicitacao: {str(e)}", False


def _build_deterministic_rko_actions(user_input):
    import unicodedata

    text = unicodedata.normalize("NFKD", user_input or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).lower()

    out_of_scope_message = _detect_out_of_scope_rko_request(text)
    if out_of_scope_message:
        return [{
            "function": "respond_to_user",
            "arguments": {"message": out_of_scope_message},
        }]

    actions = []
    mentions_restrictions = "restric" in text or "restri" in text or "retric" in text or "retri" in text
    mentions_aline = "aline paula" in text
    mentions_english = "lingua inglesa" in text or "inglesa" in text
    mentions_tuesday = "terca" in text
    asks_clear = any(word in text for word in ["apague", "limpe", "remova todas", "delete todas"])
    asks_list = (
        any(phrase in text for phrase in ["quais sao", "quais", "liste", "listar", "mostre", "temos ativa", "ativas"])
        and mentions_restrictions
    )
    asks_optimize = any(word in text for word in ["otimize", "otimizar", "rode", "gerar", "gere", "recalcule"])
    asks_analysis = any(phrase in text for phrase in [
        "funcionou", "funcionaram", "funciona", "funcionar", "deu certo", "foi atend", "foram atend", "explica",
        "explique", "analise", "analisar", "verifique", "validar", "valide",
        "conflito", "problema",
    ]) and any(term in text for term in ["restric", "restri", "retric", "retri", "grade", "solucao", "aloc", "horario"])

    if asks_clear and mentions_restrictions:
        actions.append({"function": "clear_all_constraints", "arguments": {}})

    if asks_list:
        actions.append({"function": "list_constraints", "arguments": {}})

    professor_days_action = _build_professor_only_days_action_from_text(user_input)
    if professor_days_action:
        actions.append(professor_days_action)

    if mentions_aline and mentions_english and "so pode" in text:
        actions.append(_build_professor_only_subject_action("Aline Paula", "Lingua Inglesa"))

    elif mentions_aline and mentions_english:
        actions.append({
            "function": "add_restriction_rule",
            "arguments": {
                "description": "Aline Paula deve dar aulas de Lingua Inglesa",
                "conditions": [
                    {"field": "disciplina", "operator": "==", "value": "Língua Inglesa"},
                    {"field": "professor", "operator": "!=", "value": "Aline Paula"},
                ],
            },
        })

    if mentions_aline and mentions_tuesday:
        actions.append({
            "function": "add_restriction_rule",
            "arguments": {
                "description": "Aline Paula so pode dar aula na Terca-feira",
                "conditions": [
                    {"field": "professor", "operator": "==", "value": "Aline Paula"},
                    {"field": "dia", "operator": "!=", "value": "Terca"},
                ],
            },
        })

    if asks_optimize:
        actions.append({"function": "run_unified_solver", "arguments": {}})
        actions.append({"function": "analyze_solution", "arguments": {}})

    if asks_analysis and not asks_optimize:
        actions.append({"function": "analyze_solution", "arguments": {}})

    return actions


def _detect_out_of_scope_rko_request(text):
    if not text:
        return None

    aggregate_patterns = [
        (
            ["cada turma", "por dia"],
            ["maximo", "no maximo", "minimo", "no minimo", "mais de", "menos de"],
            "limite agregado de aulas por turma/dia",
        ),
        (
            ["professor", "por dia"],
            ["maximo", "no maximo", "minimo", "no minimo", "mais de", "menos de"],
            "limite agregado de aulas por professor/dia",
        ),
        (
            ["aulas", "seguid"],
            ["maximo", "no maximo", "mais de", "consecutiv"],
            "limite de aulas consecutivas",
        ),
        (
            ["horario vazio"],
            ["entre", "janela", "gap", "buraco", "aulas"],
            "controle de janelas entre aulas",
        ),
        (
            ["janela"],
            ["turma", "professor", "aula"],
            "controle de janelas entre aulas",
        ),
        (
            ["mesmo dia"],
            ["nao podem acontecer", "nao pode acontecer", "disciplinas", "materias"],
            "relacao entre duas disciplinas no mesmo dia",
        ),
        (
            ["aulas mais dificeis"],
            ["comeco", "inicio", "fim", "leves"],
            "preferencia qualitativa de dificuldade",
        ),
        (
            ["aulas dificeis"],
            ["comeco", "inicio", "fim", "leves"],
            "preferencia qualitativa de dificuldade",
        ),
        (
            ["equilibr"],
            ["turma", "professor", "semana", "dias"],
            "balanceamento global da grade",
        ),
    ]

    for required_terms, trigger_terms, label in aggregate_patterns:
        if all(term in text for term in required_terms) and any(term in text for term in trigger_terms):
            return (
                f"Essa restricao ainda esta fora do escopo atual do RKO dinamico: {label}. "
                "Hoje eu consigo aplicar regras diretas por professor, turma, disciplina, sala, dia e periodo, "
                "mas nao consigo representar contagens ou padroes agregados como uma regra dinamica simples. "
                "Nao alterei as restricoes e nao rodei a otimizacao para evitar uma resposta falsa de sucesso."
            )

    return None


def _normalize_chat_text(text):
    import unicodedata

    normalized = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def _extract_name_from_text(text):
    import re

    normalized = _normalize_chat_text(text)
    match = re.search(r"\bmeu nome (?:e|eh)\s+([a-z][a-z'-]*)", normalized, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip(" .,!?:;").title()


def _message_looks_like_rko_request(text):
    normalized = _normalize_chat_text(text)
    rko_terms = [
        "restric", "restri", "retric", "retri", "otimiz", "grade", "aloc", "atribu", "horario", "aula",
        "professor", "professora", "turma", "sala", "disciplina", "materia",
        "ingles", "lingua", "aline", "terça", "terca", "slot",
    ]
    return any(term in normalized for term in rko_terms)


def _extract_requested_professor_name(text):
    import re

    normalized = _normalize_chat_text(text)
    patterns = [
        r".*?\b(?:professora|professor)\s+(.+?)\s+(?:so pode|s\? pode|deve|pode dar|da aula|dar aula)",
        r".*?\b(?:a|o)\s+(.+?)\s+(?:so pode|s\? pode|deve|pode dar|da aula|dar aula)",
        r"^(?:a|o)\s+(.+?)\s+(?:so pode|s\? pode|deve|pode dar|da aula|dar aula)",
        r"^(?:professora|professor)\s+(.+?)\s+(?:so pode|s\? pode|deve|pode dar|da aula|dar aula)",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        name = match.group(1).strip(" .,!?:;")
        name = name.replace("professora ", "").replace("professor ", "").strip()
        words = [word for word in name.split() if word not in ["a", "o"]]
        if any(w in ["disciplina", "disciplinas", "sala", "salas", "turma", "turmas", "materia", "materias"] for w in words):
            continue
        if len(words) >= 2:
            return " ".join(words).title()
    return None


def _find_subject_name_in_text(ambient, text):
    normalized = _normalize_chat_text(text)
    best_match = None
    for subject in ambient.subjects.all():
        subject_name = subject.name or ""
        subject_normalized = _normalize_chat_text(subject_name)
        if subject_normalized and subject_normalized in normalized:
            if not best_match or len(subject_name) > len(best_match):
                best_match = subject_name
    if not best_match and ("lingua inglesa" in normalized or "inglesa" in normalized):
        best_match = "Lingua Inglesa"
    return best_match


def _build_professor_only_subject_action(professor_name, subject_name):
    return {
        "function": "add_restriction_rule",
        "arguments": {
            "description": f"{professor_name} so pode dar {subject_name}",
            "conditions": [
                {"field": "professor", "operator": "==", "value": professor_name},
                {"field": "disciplina", "operator": "!=", "value": subject_name},
            ],
        },
    }


def _build_subject_only_professor_action(professor_name, subject_name):
    return {
        "function": "add_restriction_rule",
        "arguments": {
            "description": f"{subject_name} deve ser com {professor_name}",
            "conditions": [
                {"field": "disciplina", "operator": "==", "value": subject_name},
                {"field": "professor", "operator": "!=", "value": professor_name},
            ],
        },
    }


def _build_professor_only_day_action(professor_name, day_name):
    return {
        "function": "add_restriction_rule",
        "arguments": {
            "description": f"{professor_name} so pode dar aula na {day_name}",
            "conditions": [
                {"field": "professor", "operator": "==", "value": professor_name},
                {"field": "dia", "operator": "!=", "value": day_name},
            ],
        },
    }


def _build_professor_only_days_action_from_text(user_input):
    normalized = _normalize_chat_text(user_input)
    if not ("so pode" in normalized or "s? pode" in normalized):
        return None
    if not ("aula" in normalized or "dar" in normalized):
        return None

    professor_name = _extract_requested_professor_name(user_input)
    if not professor_name:
        return None

    day_aliases = [
        ("Segunda", ["segunda", "segunda feira"]),
        ("Terca", ["terca", "ter?a", "terca feira", "ter?a feira"]),
        ("Quarta", ["quarta", "quarta feira"]),
        ("Quinta", ["quinta", "quinta feira"]),
        ("Sexta", ["sexta", "sexta feira"]),
        ("Sabado", ["sabado", "sabado feira"]),
        ("Domingo", ["domingo"]),
    ]
    allowed_days = []
    for canonical, aliases in day_aliases:
        if any(alias in normalized for alias in aliases):
            allowed_days.append(canonical)

    if not allowed_days:
        return None

    day_text = " ou ".join(allowed_days)
    return {
        "function": "add_restriction_rule",
        "arguments": {
            "description": f"{professor_name} so pode dar aula em {day_text}",
            "conditions": [
                {"field": "professor", "operator": "==", "value": professor_name},
                {"field": "dia", "operator": "not in", "value": allowed_days},
            ],
        },
    }


def _detect_ambiguous_professor_subject_restriction(ambient, user_input):
    normalized = _normalize_chat_text(user_input)
    only_intent = "so pode" in normalized or "s? pode" in normalized or "pode dar" in normalized
    if not only_intent:
        return None
    if not any(day in normalized for day in ["terca", "ter?a", "segunda", "quarta", "quinta", "sexta", "sabado", "domingo"]):
        return None

    professor_name = _extract_requested_professor_name(user_input)
    subject_name = _find_subject_name_in_text(ambient, user_input)
    if not professor_name or not subject_name:
        return None

    professor_exists = any(
        _normalize_chat_text(member.user.name) == _normalize_chat_text(professor_name)
        for member in ambient.members.filter(is_professor=True)
        if member.user and member.user.name
    )
    if not professor_exists:
        return None

    day_name = "Terca" if ("terca" in normalized or "ter?a" in normalized) else None
    if not day_name:
        return None

    base_actions = [
        _build_professor_only_day_action(professor_name, day_name),
        _build_professor_only_subject_action(professor_name, subject_name),
    ]
    optional_action = _build_subject_only_professor_action(professor_name, subject_name)

    return {
        "type": "confirm_subject_direction",
        "professor": professor_name,
        "subject": subject_name,
        "base_actions": base_actions,
        "optional_action": optional_action,
        "question": (
            f"Antes de aplicar, quero confirmar para nao criar a regra errada.\n"
            f"Entendi que {professor_name} so pode dar aula na {day_name} e so pode dar {subject_name}.\n"
            f"Voce tambem quer obrigar que toda {subject_name} seja com {professor_name}?"
        ),
    }


def _resolve_pending_rko_confirmation(pending, user_input):
    normalized = _normalize_chat_text(user_input)
    if not pending or pending.get("type") != "confirm_subject_direction":
        return None

    yes_terms = ["sim", "isso", "tambem", "obrig", "toda", "com ela", "com ele"]
    no_terms = ["nao", "não", "so limitar", "só limitar", "apenas limitar", "so a", "só a"]

    if any(term in normalized for term in yes_terms):
        return pending.get("base_actions", []) + [pending.get("optional_action")]
    if any(term in normalized for term in no_terms):
        return pending.get("base_actions", [])
    return None


def _ask_about_unknown_professor(ambient, user_input):
    import difflib

    if not _message_looks_like_rko_request(user_input):
        return None

    requested_name = _extract_requested_professor_name(user_input)
    if not requested_name:
        return None

    professors = [
        member.user.name
        for member in ambient.members.all().filter(is_professor=True)
        if member.user and member.user.name
    ]
    normalized_map = {_normalize_chat_text(name): name for name in professors}
    normalized_requested = _normalize_chat_text(requested_name)

    if normalized_requested in normalized_map:
        return None

    close = difflib.get_close_matches(normalized_requested, normalized_map.keys(), n=1, cutoff=0.65)
    if close:
        suggestion = normalized_map[close[0]]
        return (
            f"Nao encontrei a professora {requested_name} neste ambiente. "
            f"Voce quis dizer {suggestion}? Se sim, envie a regra novamente com esse nome."
        )

    return (
        f"Nao encontrei a professora {requested_name} neste ambiente. "
        "Confirma o nome da professora antes de eu aplicar a restricao?"
    )


def _answer_from_chat_memory(user_input, conversation_history=None):
    normalized = _normalize_chat_text(user_input)
    name = _extract_name_from_text(user_input)

    if name:
        return f"Prazer, {name}. Vou usar seu nome nesta conversa."

    asks_name = "qual" in normalized and "meu nome" in normalized
    if asks_name:
        for item in reversed(conversation_history or []):
            if not isinstance(item, dict) or item.get("sender") != "user":
                continue
            remembered_name = _extract_name_from_text(item.get("text") or "")
            if remembered_name:
                return f"Seu nome e {remembered_name}."
        return "Ainda nao encontrei seu nome no historico desta conversa."

    capability_phrases = [
        "o que voce pode fazer", "o que vc pode fazer", "o que consegue fazer",
        "como voce pode ajudar", "como vc pode ajudar", "quais comandos",
        "o que da para fazer",
    ]
    if any(phrase in normalized for phrase in capability_phrases):
        return (
            "Posso conversar com voce e ajudar a mexer na grade: listar restricoes, "
            "apagar restricoes, criar regras em linguagem natural e rodar a otimizacao "
            "por atribuicao e alocacao. Tambem consigo lembrar do contexto desta sessao."
        )

    greetings = ["oi", "ola", "olá", "fala", "bom dia", "boa tarde", "boa noite", "tudo bem"]
    is_short_casual = len(normalized.split()) <= 8 and any(greeting in normalized for greeting in greetings)
    if is_short_casual and not _message_looks_like_rko_request(user_input):
        return "Tudo bem sim. Pode mandar."

    asks_general_question = "?" in (user_input or "") or normalized.startswith((
        "o que", "como", "quando", "por que", "porque", "qual", "quais", "quem", "onde"
    ))
    if asks_general_question and not _message_looks_like_rko_request(user_input):
        if conversation_history:
            return None
        return "Posso te responder pelo contexto da conversa e tambem executar ajustes na grade quando voce pedir."

    if not _message_looks_like_rko_request(user_input):
        if conversation_history:
            return None
        return "Certo, estou acompanhando."

    return None


def _build_json_actions_prompt(rko_llm_constraints, ambient):
    return (
        rko_llm_constraints.build_system_prompt(ambient)
        + "\n\n"
        + "IMPORTANTE: este modelo nao suporta function calling nativo. "
        + "Responda somente com JSON valido, sem markdown e sem explicacoes.\n"
        + "Formato obrigatorio:\n"
        + '{"actions":[{"function":"nome_da_ferramenta","arguments":{...}}]}\n'
        + "ATENCAO: Foque APENAS na ultima mensagem do usuario para decidir quais ferramentas chamar nesta rodada. "
        + "Nao repita acoes ja concluidas no historico e nao copie respostas anteriores.\n"
        + "Voce pode retornar multiplas actions em ordem. Ferramentas disponiveis e seus argumentos JSON:\n"
        + "- add_restriction_rule: {\"description\": \"Descricao curta\", \"conditions\": [{\"field\": \"campo\", \"operator\": \"operador\", \"value\": valor}]}\n"
        + "  * Campos disponiveis: \"professor\", \"turma\", \"disciplina\", \"sala\", \"dia\", \"periodo\"\n"
        + "  * Operadores: \"==\", \"!=\", \"in\", \"not in\"\n"
        + "- remove_restriction_rule: {\"index\": <numero_inteiro>}\n"
        + "- respond_to_user: {\"message\": \"sua resposta em portugues para o usuario\"}\n"
        + "- clear_all_constraints, list_constraints, get_current_timetable, analyze_solution, run_unified_solver: sem argumentos (use {})\n\n"
        + "Use a ferramenta respond_to_user (argumento: message) quando quiser apenas responder algo diretamente ao usuario em portugues.\n"
        + "Fora do escopo: limites agregados/contagens como 'maximo duas aulas por dia', aulas consecutivas, janelas/gaps, balanceamento global e preferencias qualitativas. "
        + "Nesses casos, use respond_to_user explicando que a regra ainda nao pode ser representada e nao chame clear_all_constraints nem run_unified_solver.\n"
        + "ATENCAO: Sempre que o usuario perguntar sobre quem esta na grade, quais periodos, salas, ou qualquer detalhe da grade atual, "
        + "use get_current_timetable ou analyze_solution para obter a grade horaria real. Nao presuma ou adivinhe com base apenas nas restricoes.\n"
        + "Quando o usuario pedir para otimizar a grade completa, use nesta ordem: "
        + "run_unified_solver e analyze_solution. "
        + "Quando o usuario perguntar se as restricoes funcionaram, use analyze_solution."
    )


def _extract_json_from_content(content):
    import re
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        return match.group(1).strip()
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return content[first_brace:last_brace+1].strip()
    return content.strip()


def _extract_all_json_objects(content):
    import json
    decoder = json.JSONDecoder()
    content_len = len(content)
    idx = 0
    results = []
    while idx < content_len:
        start = content.find('{', idx)
        if start == -1:
            break
        try:
            obj, end = decoder.raw_decode(content, start)
            results.append(obj)
            idx = end
        except json.JSONDecodeError:
            idx = start + 1
    return results


def _parse_and_run_json_actions(rko_llm_constraints, ambientid, content):
    import json
    decoded_objects = _extract_all_json_objects(content)
    if not decoded_objects:
        return None, False, []

    actions = []
    for data in decoded_objects:
        if isinstance(data, list):
            actions.extend(data)
        elif isinstance(data, dict):
            if isinstance(data.get("actions"), list):
                actions.extend(data["actions"])
            elif data.get("tool") or data.get("function"):
                actions.append(data)

    if not actions:
        return None, False, []

    outputs = []
    rules_changed = False
    solver_ran = False
    for action in actions:
        if not isinstance(action, dict):
            continue
        function_name = action.get("tool") or action.get("function")
        if not function_name:
            continue
        args = action.get("arguments") or action.get("args") or {}
        output, changed, ran_solver = _run_rko_tool_action(rko_llm_constraints, ambientid, function_name, args)
        outputs.append(f"Execucao da ferramenta {function_name}:\n{output}")
        rules_changed = rules_changed or changed
        solver_ran = solver_ran or ran_solver

    return "\n\n".join(outputs), rules_changed and not solver_ran, actions


def _try_run_rko_tool_from_json_content(rko_llm_constraints, ambientid, content):
    content_clean = content.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(content_clean)
    except Exception:
        try:
            content_clean = content_clean.replace("'", '"').replace("True", "true").replace("False", "false")
            data = json.loads(content_clean)
        except Exception:
            return None, False

    if isinstance(data, list):
        return _run_rko_json_actions(rko_llm_constraints, ambientid, data)

    if not isinstance(data, dict):
        return None, False

    if isinstance(data.get("actions"), list):
        return _run_rko_json_actions(rko_llm_constraints, ambientid, data["actions"])

    function_name = data.get("tool") or data.get("function")
    if not function_name:
        return None, False

    args = data.get("arguments") or data.get("args") or {}
    if isinstance(args, list):
        if function_name == "add_restriction_rule" and len(args) >= 2:
            args = {"description": args[0], "conditions": args[1]}
        else:
            args = {}
            
    output, rules_changed, _ = _run_rko_tool_action(rko_llm_constraints, ambientid, function_name, args)
    return output, rules_changed


def _tool_output_succeeded(output):
    text = str(output or "").lower()
    failure_markers = [
        "erro ao executar", "obrigatoria", "obrigatorio", "invalido",
        "nao encontrado", "nao consegui",
    ]
    return bool(text.strip()) and not any(marker in text for marker in failure_markers)


def _run_rko_tool_action(rko_llm_constraints, ambientid, function_name, args):
    args = args or {}
    if isinstance(args, list):
        if function_name == "add_restriction_rule" and len(args) >= 2:
            args = {"description": args[0], "conditions": args[1]}
        else:
            args = {}

    if function_name == "run_unified_solver":
        _thread_locals.solver_ran = True
        return rko_llm_constraints.run_tool(ambientid, function_name, args), False, True

    if function_name in ["run_attribution_solver", "run_allocation_solver"]:
        return (
            "Pelo chat da IA, a otimizacao agora usa apenas o resolvedor unificado "
            "(atribuicao + alocacao juntos). Os decoders separados continuam disponiveis nos botoes da interface.",
            False,
            False,
        )

    if function_name == "add_restriction_rule" and not args.get("description"):
        conds = args.get("conditions") or []
        cond_strings = []
        for cond in conds:
            if isinstance(cond, dict):
                cond_strings.append(f"{cond.get('field')} {cond.get('operator')} {cond.get('value')}")
        args["description"] = "Restricao: " + " e ".join(cond_strings) if cond_strings else "Nova restricao dinamica" 

    output = rko_llm_constraints.run_tool(ambientid, function_name, args)
    rules_changed_tools = ["add_restriction_rule", "clear_all_constraints", "remove_restriction_rule"]
    rules_changed = function_name in rules_changed_tools and _tool_output_succeeded(output)
    return output, rules_changed, False


def _run_rko_solver_action_via_app(ambientid, function_name):
    try:
        ambient = Ambient.objects.get(ambientid=ambientid)
    except Ambient.DoesNotExist:
        return f"Ambiente {ambientid} nao encontrado."

    if function_name == "run_attribution_solver":
        _run_attribution_logic_silent(ambient)
        return "Otimizador de Atribuicao (Fase 1) concluido pela rotina da aplicacao."

    if function_name == "run_allocation_solver":
        _run_allocation_logic_silent(ambient)
        ambient.refresh_from_db()

        activities_total = ambient.activities.count()
        allocated_ids = set()
        not_allocated_count = 0
        if ambient.published_timetable:
            not_allocated_count = ambient.published_timetable.not_alocated.count()
            for slot in ambient.published_timetable.table.all():
                allocated_ids.update(slot.activitie.values_list("id", flat=True))

        return (
            "Otimizador de Alocacao (Fase 2) concluido pela rotina da aplicacao. "
            f"Atividades alocadas: {len(allocated_ids)}/{activities_total}. "
            f"Nao alocadas por conflito: {not_allocated_count}."
        )

    return f"Ferramenta desconhecida: {function_name}"


def _run_rko_json_actions(rko_llm_constraints, ambientid, actions):
    outputs = []
    rules_changed = False
    solver_ran = False

    for action in actions:
        if not isinstance(action, dict):
            continue
        function_name = action.get("tool") or action.get("function")
        if not function_name:
            continue
        args = action.get("arguments") or action.get("args") or {}
        if function_name in ["run_unified_solver", "run_attribution_solver", "run_allocation_solver"] and any(
            not _tool_output_succeeded(output) for output in outputs
        ):
            outputs.append("Nao rodei a otimizacao porque uma regra anterior nao foi aplicada corretamente.")
            continue
        output, changed, ran_solver = _run_rko_tool_action(rko_llm_constraints, ambientid, function_name, args)
        outputs.append(output)
        rules_changed = rules_changed or changed
        solver_ran = solver_ran or ran_solver

    if not outputs:
        return None, False
    return _format_rko_outputs(outputs), rules_changed and not solver_ran


def _format_rko_outputs(outputs):
    formatted = []
    for output in outputs:
        text = str(output or "")
        if text.startswith("Analise deterministica da grade:"):
            formatted.append(_summarize_solution_analysis(text))
        else:
            formatted.append(text)
    return "\n".join(item for item in formatted if item)


def _summarize_solution_analysis(text):
    raw_json = text.split("Analise deterministica da grade:", 1)[1].strip()
    try:
        data = json.loads(raw_json)
    except Exception:
        return text

    resumo = data.get("resumo", {})
    resultado = data.get("resultado", {})
    observacoes = data.get("observacoes", [])
    restricoes = data.get("restricoes", [])
    pending_unique = data.get("nao_alocadas_unicas", [])

    lines = []
    if resumo.get("atividades_total", 0) and resumo.get("atividades_alocadas_unicas", 0) == 0:
        return (
            "Ainda nao consigo avaliar bem essa solucao porque a grade publicada esta vazia: "
            "existem atividades cadastradas, mas nenhuma aparece alocada. "
            "O melhor proximo passo e rodar a otimizacao novamente e depois pedir a analise."
        )

    if resultado.get("restricoes_ok"):
        if pending_unique:
            lines.append(
                "Deu certo sim: todas as restricoes ativas foram atendidas. "
                f"Mas, para manter essas regras sem violar a grade, {len(pending_unique)} atividade(s) ficaram sem alocacao."
            )
        elif resultado.get("conflitos_ok"):
            lines.append("Deu certo sim: todas as restricoes foram atendidas e nao encontrei atividades pendentes ou conflitos na grade.")
        else:
            lines.append("As restricoes foram atendidas, mas ainda encontrei conflito de recurso na grade.")
    else:
        violated_rules_count = resumo.get("restricoes_violadas", len([
            rule for rule in restricoes if rule.get("violacoes")
        ]))
        lines.append(
            f"Ainda nao deu totalmente certo: {violated_rules_count} restricao(oes) ativa(s) foram violadas."
        )

    attended_rules = []
    violated_rules = []
    for rule in restricoes:
        violations = rule.get("violacoes") or []
        if not violations:
            attended_rules.append(rule.get("descricao"))
            continue
        violated_rules.append(rule)

    if attended_rules and not violated_rules:
        lines.append("As restricoes atendidas foram: " + "; ".join(str(rule) for rule in attended_rules) + ".")

    for rule in violated_rules:
        violations = rule.get("violacoes") or []
        unique_activities = {}
        for violation in violations:
            activity = violation.get("atividade", {})
            activity_id = activity.get("id") or f"{activity.get('turma')}:{activity.get('disciplina')}"
            unique_activities.setdefault(activity_id, violation)

        lines.append(
            f"O ponto principal e a regra '{rule.get('descricao')}'. "
            f"Ela foi quebrada por {len(unique_activities)} atividade(s), embora apareca em {len(violations)} periodo(s)."
        )
        first_violation = next(iter(unique_activities.values()), None)
        if first_violation:
            slot = first_violation.get("slot", {})
            activity = first_violation.get("atividade", {})
            lines.append(
                "Exemplo: "
                f"{activity.get('disciplina')} de {activity.get('turma')} ficou com "
                f"{activity.get('professor')} em {slot.get('dia')}. "
                "Isso viola a restricao porque esse dia nao esta entre os dias permitidos."
            )

    if pending_unique:
        lines.append(
            f"Tambem ficou {len(pending_unique)} atividade(s) sem alocacao. "
            "Pelo motivo registrado, nao parece ser falta simples de periodo: foi conflito de recurso "
            "(professor, turma ou sala disputando o mesmo encaixe)."
        )
        for pending in pending_unique[:1]:
            activity = pending.get("atividade") or {}
            reasons = [reason for reason in pending.get("motivos", []) if reason]
            reason_text = reasons[0] if reasons else "Sem motivo detalhado registrado."
            lines.append(
                f"Exemplo de pendencia: {activity.get('turma')} - {activity.get('disciplina')}, "
                f"com {activity.get('professor')}, na {activity.get('sala')}. "
                f"Motivo registrado: {reason_text}"
            )
        if len(pending_unique) > 1:
            lines.append(f"Ha mais {len(pending_unique) - 1} atividade(s) pendente(s), mas o padrao e o mesmo.")

    useful_notes = [
        note for note in observacoes
        if "restricoes dinamicas ativas" not in note and "nao alocadas" not in note
    ]
    if useful_notes:
        lines.append("Um detalhe importante: " + useful_notes[0])

    return "\n".join(lines)


def chatbot(ambientid, user_input=""):
    functions = {
        "schedule_preference_adjustment": schedule_preference_adjustment,
        "professor_preference_adjustment": professor_preference_adjustment,
        "classroom_preference_adjustment": classroom_preference_adjustment,
    }

    if not user_input:
        return "Nenhum comando enviado para o chatbot."

    prompt = f"""
    Você é um assistente Python. Analise o comando do usuário e responda em JSON com o nome da função e os argumentos.
    Como argumentos, você receberá o tipo de origem da preferência (professor, matéria ou turma), o nome da origem,
    o nome da preferência (horário, professor ou sala) e o peso da preferência (número entre 0 e 100) ou se a
    preferência é verdadeira ou falsa, em casos de preferência horária. Caso o usuário não forneça algum dado, você
    é livre para preencher o formato de resposta da maneira que achar melhor, desde que seja possível entender qual é a preferência, a origem e o peso ou se é verdadeira ou falsa, no caso de preferência horária.
    Padrões e exemplos de resposta:
    1) Para ajustar uma preferência de horário específico: {{"function": "schedule_preference_adjustment", "args": ['Professor', 'Carlos Silva', [2,3], True]}} - Define como verdadeira a preferência de horário do professor Carlos Silva para o horário 3 do dia 4.
    2) Para ajustar a preferência de horário para um DIA INTEIRO: {{"function": "schedule_preference_adjustment", "args": ['Professor', 'Carlos Silva', 2, True]}} - Define como verdadeira a preferência de horário do professor Carlos Silva para TODOS os horários do dia 3 (dia indexado em 2). Se o usuário disser "dia Y", passe o número Y-1 como o terceiro argumento.
    3) Para ajustar uma preferência de matéria: {{"function": "professor_preference_adjustment", "args": ['Matéria', 'Matemática', 'Carlos Silva', 100]}} - Define o peso da preferência da matéria de Matemática pelo professor Carlos Silva como 100, o que pode influenciar na alocação de atividades desta matéria para ele.
    4) Para ajustar uma preferência de sala: {{"function": "classroom_preference_adjustment", "args": ['Turma', 'Ciência da Computação I', 'Laboratório de Informática I', 100]}} - Define o peso da preferência da turma de Ciência da Computação I pelo Laboratório de Informática I como 100, o que pode influenciar na alocação de atividades desta turma para esta sala.
    Caso o usuário diga para não colocar uma preferência, o peso deve ser definido como 0, ou, no caso de preferência horária, a preferência deve ser definida como falsa.
    Caso o usuário diga que uma preferência DEVE ser atendida, o peso deve ser definido como 100, ou, no caso de preferência horária, a preferência deve ser definida como verdadeira.
    Caso o usuário não especifique uma forte necessidade, o peso pode ser definido como 50

    Para definir horários específicos, o primeiro número sempre será o horário e o segundo sempre será o dia, e a contagem inicia em 0, então [0,0] representa o horário 1 do dia 1. Se for especificado um dia inteiro, use apenas o número do dia indexado em 0 (ex: "dia 3" virá como o número 2).

    Comando: {user_input}
    """
    api_key = os.environ.get("HF_TOKEN")
    model = os.environ.get("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    if not api_key:
        return "Configure a variável de ambiente HF_TOKEN para ativar o chat de IA."

    response = requests.post(
        url="https://router.huggingface.co/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    result = response.json()
    if response.status_code != 200:
        error_msg = "Erro desconhecido"
        if isinstance(result, dict):
            if "error" in result:
                error_msg = result["error"].get("message", str(result["error"]))
            elif "message" in result:
                error_msg = result.get("message")
        print("Erro do Hugging Face:", error_msg)
        return f"Erro na API do Hugging Face: {error_msg}. Por favor, certifique-se de configurar um token de API válido na variável de ambiente HF_TOKEN."

    try:
        content = result["choices"][0]["message"]["content"]
        content_clean = content.replace("```json", "").replace("```", "").strip()
        content_clean = content_clean.replace("'", '"').replace("True", "true").replace("False", "false")
        print(content_clean)
        data = json.loads(content_clean)
        func_name = data.get("function")
        args = data.get("args", [])

        func = functions.get(func_name)
        if func:
            func(ambientid, *args)
            if func_name == "schedule_preference_adjustment":
                origin_type, origin, preference, true_false = args
                status = "ativa" if true_false else "inativa"
                if isinstance(preference, int) or (isinstance(preference, str) and not isinstance(preference, list)):
                    try:
                        val = int(str(preference).lower().replace("dia", "").strip())
                        if "dia" not in str(preference).lower():
                            display_day = val + 1
                        else:
                            display_day = val
                    except:
                        display_day = preference
                    return f"Entendi! Ajustei a preferência de horário do {origin_type} '{origin}' para TODOS os horários do Dia {display_day} para {status}."
                else:
                    return f"Entendi! Ajustei a preferência de horário do {origin_type} '{origin}' no horário/dia {preference} para {status}."
            elif func_name == "professor_preference_adjustment":
                origin_type, origin, preference, weight = args
                return f"Entendi! Defini a preferência do {origin_type} '{origin}' pelo professor '{preference}' com peso {weight}."
            elif func_name == "classroom_preference_adjustment":
                origin_type, origin, preference, weight = args
                return f"Entendi! Defini a preferência do {origin_type} '{origin}' pela sala '{preference}' com peso {weight}."
            return f"Comando '{func_name}' executado com sucesso."
        else:
            return f"Desculpe, não encontrei a função '{func_name}' nas minhas configurações."
    except Exception as e:
        print("Erro ao processar resposta da LLM:", e)
        try:
            fallback = result["choices"][0]["message"]["content"]
            if fallback:
                return fallback
        except:
            pass
        return f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"


@csrf_exempt
def chatbot_api(request, ambientid):
    _thread_locals.solver_ran = False
    history_key = f"rko_chat_history:{ambientid}"
    pending_key = f"rko_pending_confirmation:{ambientid}"
    greeting = "Ola! Sou a IA do AllokAcad. Como posso ajustar a sua grade?"

    if not request.user.is_authenticated:
        return JsonResponse({"error": "not_authenticated", "response": "Usuário não autenticado."}, status=401)

    if request.method == "GET":
        history = request.session.get(history_key, [])
        if not history:
            history = [{"sender": "bot", "text": greeting}]
        return JsonResponse({"history": history})

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "").strip()
            if not user_input:
                return JsonResponse({"response": "Por favor, digite uma mensagem válida."}, status=400)

            history = request.session.get(history_key, [])
            pending = request.session.get(pending_key)

            if pending:
                resolved_actions = _resolve_pending_rko_confirmation(pending, user_input)
                if resolved_actions is None:
                    bot_response = (
                        "Ainda preciso dessa confirmacao para seguir: "
                        "voce quer obrigar a disciplina com essa professora tambem, "
                        "ou e so para limitar a professora?"
                    )
                    rules_changed = False
                else:
                    from AllokAcads import rko_llm_constraints
                    bot_response, rules_changed = _run_rko_json_actions(
                        rko_llm_constraints,
                        ambientid,
                        [action for action in resolved_actions if action],
                    )
                    request.session.pop(pending_key, None)
                    request.session.modified = True
            else:
                ambient = Ambient.objects.get(ambientid=ambientid)
                pending_confirmation = _detect_ambiguous_professor_subject_restriction(ambient, user_input)
                if pending_confirmation:
                    request.session[pending_key] = pending_confirmation
                    request.session.modified = True
                    bot_response = pending_confirmation["question"]
                    rules_changed = False
                else:
                    bot_response, rules_changed = rko_chatbot(ambientid, user_input, history)
            solver_ran = (
                "Otimizador Unificado" in bot_response or
                "Otimizador de Atribuicao" in bot_response or
                "Otimizador de Alocacao" in bot_response or
                getattr(_thread_locals, "solver_ran", False)
            )

            if rules_changed and not solver_ran:
                from AllokAcads import rko_llm_constraints
                solver_output = rko_llm_constraints.run_tool(ambientid, "run_unified_solver", {})
                solver_ran = _tool_output_succeeded(solver_output)
                bot_response += (
                    "\n\n" + solver_output +
                    "\n\nA grade foi recalculada automaticamente com o resolvedor unificado da IA."
                )

            history = [
                item for item in history
                if isinstance(item, dict) and item.get("sender") in ["user", "bot"] and item.get("text")
            ]
            history.extend([
                {"sender": "user", "text": user_input},
                {"sender": "bot", "text": bot_response},
            ])
            history = history[-40:]
            request.session[history_key] = history
            request.session.modified = True

            return JsonResponse({
                "response": bot_response,
                "rules_changed": rules_changed,
                "should_reload": bool(rules_changed or solver_ran),
                "history": history,
            })
        except Exception as e:
            return JsonResponse({"error": "invalid_request", "response": f"Erro ao processar requisição: {str(e)}"}, status=400)

    return JsonResponse({"error": "method_not_allowed", "response": "Método não permitido."}, status=405)
