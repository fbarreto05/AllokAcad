from urllib import request
from django.shortcuts import render, redirect
from django.conf import settings
import random, os, datetime, time
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

        if ambient.members.filter(user = user) and member.admin_type.can_run_atribuition:
            #Limpa as atividades para iniciar uma nova atribuição.
            ambient.activities.all().delete()
            ambient.activities.clear()
            ambient.save()
            rooms = ambient.classrooms.all()
            for room in rooms:
                room.num_uses = 0
                room.save()
            rooms = ambient.classrooms.all()
            professors = ambient.members.all().filter(is_professor = True)
            for professor in professors:
                professor.num_uses = 0
                professor.save()
            #Recria as atividades.
            classes = ambient.classes.all()
            for aclass in classes:
                necessary_subjects = aclass.necessary_subjects.all()
                for subject in necessary_subjects:
                    activitie = Activitie(tclass = aclass, tsubject = subject.subject, activities_qtd = subject.periods)
                    activitie.save()
                    ambient.activities.add(activitie)
                    ambient.save()

            #Inicia a atribuição de salas. Para cada atividade, são listadas as salas ideais para a turma e para a disciplina, essas listas são iteradas, analisando o peso 
            #de cada preferência a cada iteração, e a preferência que tiver o maior peso é selecionada.
            activities = ambient.activities.all()
            for activitie in activities:
                class_rooms = activitie.tclass.ideal_classrooms.all().order_by("-classroom_weight", "classroom__num_uses")
                subjects_rooms = activitie.tsubject.ideal_classrooms.all().order_by("-classroom_weight", "classroom__num_uses")
                highest_weight = 0
                chosen_room = None
                chosen_conflitant_classroom = None

                for room in class_rooms:
                    class_classroom_weight = room.classroom_weight
                    subject_classroom_weight = subjects_rooms.get(classroom = room.classroom).classroom_weight if subjects_rooms.filter(classroom = room.classroom).exists() else 1
                    highest_subject_classroom_weight = subjects_rooms.get(classroom = chosen_room).classroom_weight if subjects_rooms.filter(classroom = chosen_room).exists() else 1
                    highest_class_classroom_weight = class_rooms.get(classroom = chosen_room).classroom_weight if class_rooms.filter(classroom = chosen_room).exists() else 1

                    #Verifica se existem conflitos de horário
                    timetable = list(ambient.published_timetable.table.all())
                    activities_with_classroom = list(ambient.activities.filter(tclassroom = room.classroom))
                    activities_with_classroom.append(activitie)
                    conflitant_classroom = check_conflitant_schedules_classroom(activities_with_classroom, timetable, room.classroom)

                    weight = subject_classroom_weight + class_classroom_weight

                    #Se atender aos requisitos, define como a atividade escolhida, assim como seu peso e uma possível atividade conflitante para o caso de precisar ser trocada.
                    if ((highest_subject_classroom_weight < 100 and highest_class_classroom_weight < 100) or (subject_classroom_weight >= 100 or class_classroom_weight >= 100)) and weight > highest_weight and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                        highest_weight = weight
                        chosen_room = room.classroom
                        chosen_conflitant_classroom = conflitant_classroom

                for room in subjects_rooms:
                    #Verifica se existem conflitos de horário
                    subject_classroom_weight = room.classroom_weight
                    highest_class_classroom_weight = class_rooms.get(classroom = chosen_room).classroom_weight if class_rooms.filter(classroom = chosen_room).exists() else 1
                    highest_subject_classroom_weight = subjects_rooms.get(classroom = chosen_room).classroom_weight if subjects_rooms.filter(classroom = chosen_room).exists() else 1
                
                    timetable = list(ambient.published_timetable.table.all())
                    activities_with_classroom = list(ambient.activities.filter(tclassroom = room.classroom))
                    activities_with_classroom.append(activitie)
                    conflitant_classroom = check_conflitant_schedules_classroom(activities_with_classroom, timetable, room.classroom)

                    weight = subject_classroom_weight

                    #Se atender aos requisitos, define como a atividade escolhida, assim como seu peso e uma possível atividade conflitante para o caso de precisar ser trocada.
                    if ((highest_subject_classroom_weight < 100 and highest_class_classroom_weight < 100) or (subject_classroom_weight >= 100 or class_classroom_weight >= 100)) and weight > highest_weight and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                        highest_weight = weight
                        chosen_room = room.classroom
                        chosen_conflitant_classroom = conflitant_classroom
                
                #Após as iterações, atribui a sala escolhida definitivamente, caso os requisitos sejam atendidos. Se houver uma atividade conflitante, ela também é removida agora.
                if(highest_weight > 0 and chosen_room != None):
                    activitie.tclassroom = chosen_room
                    activitie.classroom_weight = highest_weight
                    activitie.save()
                    chosen_room.num_uses += activitie.activities_qtd
                    chosen_room.save()

                    if isinstance(chosen_conflitant_classroom, Activitie):
                        tclassroom = chosen_conflitant_classroom.tclassroom
                        tclassroom.num_uses -= chosen_conflitant_classroom.activities_qtd
                        tclassroom.save()
                        chosen_conflitant_classroom.tclassroom = None   
                        chosen_conflitant_classroom.classroom_weight = 0
                        chosen_conflitant_classroom.save()

            #Aqui as salas passam por um reajuste para garantir que salas que tenham um uso muito acima da média liberem algumas atividades para outras. Caso haja uma troca, o processo é repetido, com limite de 20 repetições.
            swap = True
            it = 0
            #Este while se repe no máximo dez vezes, enquanto houverem trocas de atividade que deixem uma atividade sem sala, dando a chance de fazer uma nova atribuição para esta atividade
            while swap and it < 10:
                swap = False
                it += 1
                #Calcula a ocupação média
                average_occupation = 0
                for room in rooms:
                    average_occupation += room.num_uses   
                if(len(rooms)):
                    average_occupation = average_occupation/len(rooms)

                for activitie in activities:
                    if activitie.tclassroom: 
                        current_subject_classroom_weight = subjects_rooms.get(classroom = activitie.tclassroom).classroom_weight if subjects_rooms.filter(classroom = activitie.tclassroom).exists() else 1
                        current_class_classroom_weight = class_rooms.get(classroom = activitie.tclassroom).classroom_weight if class_rooms.filter(classroom = activitie.tclassroom).exists() else 1
                        #Itera para cada atividade, se sua sala tiver um uso acima da média, a atribuição é refeita, removendo a sala atribuída da lista e considerando apenas as outras atividades. 
                        #Repetindo a mesma lógica de comparação de pesos e escolha de sala.
                        class_rooms = activitie.tclass.ideal_classrooms.all().order_by("-classroom_weight", "classroom__num_uses")
                        subjects_rooms = activitie.tsubject.ideal_classrooms.all().order_by("-classroom_weight", "classroom__num_uses")
                        second_class_rooms = class_rooms.exclude(classroom=activitie.tclassroom)
                        second_subject_rooms = subjects_rooms.exclude(classroom=activitie.tclassroom)

                        if activitie.tclassroom.num_uses > average_occupation:
                            highest_weight = 0
                            chosen_room = None
                            chosen_conflitant_classroom = None

                            for room in second_class_rooms:
                                class_classroom_weight = room.classroom_weight
                                subject_classroom_weight = second_subject_rooms.get(classroom = room.classroom).classroom_weight if second_subject_rooms.filter(classroom = room.classroom).exists() else 1
                                highest_subject_classroom_weight = subjects_rooms.get(classroom = chosen_room).classroom_weight if subjects_rooms.filter(classroom = chosen_room).exists() else 1
                                highest_class_classroom_weight = class_rooms.get(classroom = chosen_room).classroom_weight if class_rooms.filter(classroom = chosen_room).exists() else 1

                                timetable = list(ambient.published_timetable.table.all())
                                activities_with_classroom = list(ambient.activities.filter(tclassroom = room.classroom))
                                activities_with_classroom.append(activitie)
                                conflitant_classroom = check_conflitant_schedules_classroom(activities_with_classroom, timetable, room.classroom)

                                weight = subject_classroom_weight + class_classroom_weight

                                #Aqui, verifica também se a diferença de uso entre a sala atualmente atribuída e a sala candidata é suficiente para justificar a troca, para evitar que haja trocas que não resultem em uma melhora significativa na ocupação das salas.
                                if (((highest_subject_classroom_weight < 100 and highest_class_classroom_weight < 100) and (current_class_classroom_weight < 100 and current_subject_classroom_weight < 100)) or (subject_classroom_weight >= 100 or class_classroom_weight >= 100)) and weight > highest_weight and activitie.tclassroom.num_uses - room.classroom.num_uses > activitie.activities_qtd and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                                    highest_weight = weight
                                    chosen_room = room.classroom
                                    chosen_conflitant_classroom = conflitant_classroom

                            for room in second_subject_rooms:
                                subject_classroom_weight = room.classroom_weight
                                highest_subject_classroom_weight = subjects_rooms.get(classroom = chosen_room).classroom_weight if subjects_rooms.filter(classroom = chosen_room).exists() else 1
                                highest_class_classroom_weight = class_rooms.get(classroom = chosen_room).classroom_weight if class_rooms.filter(classroom = chosen_room).exists() else 1

                                timetable = list(ambient.published_timetable.table.all())
                                activities_with_classroom = list(ambient.activities.filter(tclassroom = room.classroom))
                                activities_with_classroom.append(activitie)
                                conflitant_classroom = check_conflitant_schedules_classroom(activities_with_classroom, timetable, room.classroom)

                                weight = subject_classroom_weight

                                #Aqui, verifica também se a diferença de uso entre a sala atualmente atribuída e a sala candidata é suficiente para justificar a troca, para evitar que haja trocas que não resultem em uma melhora significativa na ocupação das salas.
                                if (((highest_subject_classroom_weight < 100 and highest_class_classroom_weight < 100) and (current_class_classroom_weight < 100 and current_subject_classroom_weight < 100)) or (subject_classroom_weight >= 100 or class_classroom_weight >= 100))and weight > highest_weight and activitie.tclassroom.num_uses - room.classroom.num_uses > activitie.activities_qtd and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom and not isinstance(chosen_conflitant_classroom, Activitie):
                                    highest_weight = weight
                                    chosen_room = room.classroom
                                    chosen_conflitant_classroom = conflitant_classroom

                            if(highest_weight > 0 and chosen_room != None):
                                classroom_save = activitie.tclassroom
                                classroom_save.num_uses -= activitie.activities_qtd
                                classroom_save.save()
                                swap = True

                                activitie.tclassroom = chosen_room
                                activitie.classroom_weight = highest_weight
                                chosen_room.num_uses += activitie.activities_qtd
                                chosen_room.save()
                                activitie.save()

                            #Caso não tenha escolhido uma boa sala e a preferência pela sala atual seja < 100, vai procurar uma nova sala semelhante, que tenha o mesmo tipo que a atual.
                            #Repetindo a mesma lógica de comparação de pesos e escolha de sala de sempre.
                            else: 
                                chosen_conflitant_classroom = None
                                chosen_room = None
                                similar_rooms = Classroom.objects.filter(classroom_type = activitie.tclassroom.classroom_type).order_by('num_uses')
                                weight = 0
                                highest_weight = 0
                                
                                
                                for room in similar_rooms:
                                    #Puxa os pesos de preferência pela sala atual, para comparar e escolher o maior peso
                                    subject_classroom_weight = subjects_rooms.get(classroom = room).classroom_weight if subjects_rooms.filter(classroom = room).exists() else 1
                                    class_classroom_weight = class_rooms.get(classroom = room).classroom_weight if class_rooms.filter(classroom = room).exists() else 1
                                    highest_subject_classroom_weight = subjects_rooms.get(classroom = chosen_room).classroom_weight if subjects_rooms.filter(classroom = chosen_room).exists() else 1
                                    highest_class_classroom_weight = class_rooms.get(classroom = chosen_room).classroom_weight if class_rooms.filter(classroom = chosen_room).exists() else 1

                                    weight = subject_classroom_weight + class_classroom_weight

                                    #Verifica se há conflitos de horário
                                    timetable = list(ambient.published_timetable.table.all())
                                    activities_with_classroom = list(ambient.activities.filter(tclassroom = room))
                                    activities_with_classroom.append(activitie)
                                    conflitant_classroom = check_conflitant_schedules_classroom(activities_with_classroom, timetable, room)
                                    #Escolhe a sala se as condições forem atendidas
                                    if ((highest_subject_classroom_weight < 100 and highest_class_classroom_weight < 100) or (subject_classroom_weight >= 100 or class_classroom_weight >= 100)) and weight > highest_weight and activitie.tclassroom.num_uses - room.num_uses > activitie.activities_qtd and room.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom and not isinstance(chosen_conflitant_classroom, Activitie):
                                        highest_weight = weight
                                        chosen_room = room
                                        chosen_conflitant_classroom = conflitant_classroom

                                #Consolida a atribuição
                                if(highest_weight > 0 and chosen_room != None):
                                    classroom_save = activitie.tclassroom
                                    classroom_save.num_uses -= activitie.activities_qtd
                                    classroom_save.save()
                                    swap = True

                                    activitie.tclassroom = chosen_room
                                    activitie.classroom_weight = highest_weight
                                    chosen_room.num_uses += activitie.activities_qtd
                                    chosen_room.save()
                                    activitie.save()

            #Ao fim do ajuste, verifica se alguma atividade ficou sem uma sala, em caso positivo, lhe atribui uma aleatória, priorizando salas semelhantes e aquelas que tiverem menos ocupação
            #Repetindo a mesma lógica de comparação de pesos e escolha de sala de sempre.
            not_atribuited_activities = ambient.activities.filter(tclassroom = None)
            for activitie in not_atribuited_activities:
                # Redefine as preferências de salas para a atividade atual
                class_rooms = activitie.tclass.ideal_classrooms.all()
                subjects_rooms = activitie.tsubject.ideal_classrooms.all()
                
                # Conta a frequência de cada tipo de sala nas preferências
                classroom_types_count = {}
                for pref in class_rooms:
                    room_type = pref.classroom.classroom_type
                    if room_type:
                        classroom_types_count[room_type] = classroom_types_count.get(room_type, 0) + 1
                for pref in subjects_rooms:
                    room_type = pref.classroom.classroom_type
                    if room_type:
                        classroom_types_count[room_type] = classroom_types_count.get(room_type, 0) + 1
                
                # Identifica o tipo de sala mais preferido
                most_preferred_type = max(classroom_types_count, key=classroom_types_count.get) if classroom_types_count else None
                
                # Ordena as salas priorizando o tipo mais preferido e depois o número de usos
                random_rooms = sorted(
                    ambient.classrooms.all(),
                    key=lambda room: (
                        0 if (most_preferred_type and room.classroom_type == most_preferred_type) else 1,
                        room.num_uses
                    )
                )
                
                weight = 0
                highest_weight = 0
                chosen_room = None
                chosen_conflitant_classroom = None

                for random_room in random_rooms:
                    #Puxa os pesos de preferência pela sala atual, para comparar e escolher o maior peso
                    subject_classroom_weight = subjects_rooms.get(classroom = random_room).classroom_weight if subjects_rooms.filter(classroom = random_room).exists() else 1
                    class_classroom_weight = class_rooms.get(classroom = random_room).classroom_weight if class_rooms.filter(classroom = random_room).exists() else 1
                    highest_subject_classroom_weight = subjects_rooms.get(classroom = chosen_room).classroom_weight if subjects_rooms.filter(classroom = chosen_room).exists() else 1
                    highest_class_classroom_weight = class_rooms.get(classroom = chosen_room).classroom_weight if class_rooms.filter(classroom = chosen_room).exists() else 1
                    weight = subject_classroom_weight + class_classroom_weight

                    timetable = list(ambient.published_timetable.table.all())
                    activities_with_classroom = list(ambient.activities.filter(tclassroom = random_room))
                    activities_with_classroom.append(activitie)
                    conflitant_classroom = check_conflitant_schedules_classroom(activities_with_classroom, timetable, random_room)

                    if ((highest_subject_classroom_weight < 100 and highest_class_classroom_weight < 100) or (subject_classroom_weight >= 100 or class_classroom_weight >= 100)) and weight > highest_weight and random_room.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                        highest_weight = weight
                        chosen_room = random_room
                        chosen_conflitant_classroom = conflitant_classroom
                        
                if(highest_weight > 0 and chosen_room != None):
                    activitie.tclassroom = chosen_room
                    activitie.classroom_weight = 0
                    activitie.save()
                    chosen_room.num_uses += activitie.activities_qtd
                    chosen_room.save()
                    
                    if isinstance(chosen_conflitant_classroom, Activitie):
                        tclassroom = chosen_conflitant_classroom.tclassroom
                        tclassroom.num_uses -= chosen_conflitant_classroom.activities_qtd
                        tclassroom.save()
                        chosen_conflitant_classroom.tclassroom = None   
                        chosen_conflitant_classroom.classroom_weight = 0
                        chosen_conflitant_classroom.save() 

            #inicio da atribuição de professores
            activities = ambient.activities.all()
            count = 0
            repeat = True
            #Este while se repe no máximo dez vezes, enquanto houverem trocas de atividade que deixem uma atividade sem professor, dando a chance de fazer uma nova atribuição para esta atividade
            while count < 10 and repeat == True:
                count += 1
                repeat = False
                for activitie in activities:
                    #Começa selecionando as preferências da turma e da disciplina por professores, e iniciando as varíaveis de peso e professor escolhido para fazer as comparações.
                    #Além de uma variável de controle que indica se houve uma troca de professor, para garantir que o professor trocado seja desalocado dessa atividade posteriormente.
                    class_professors = None
                    subjects_professors = None
                    if activitie.tclass.favorite_professors:
                        class_professors = activitie.tclass.favorite_professors.all().order_by("-professor_weight", "professor__num_uses")
                    if activitie.tsubject.favorite_professors:
                        subjects_professors = activitie.tsubject.favorite_professors.all().order_by("-professor_weight", "professor__num_uses")
                    highest_weight = 0
                    chosen_professor = None  
                    chosen_conflitant_professor = None              
                    swap = 0
                    swapAct = None
                    
                    #Itera sobre as preferências de turma por cada professor. Primeiro, coleta seus pesos para fins de comparação, depois, verifica se ele já ultrapassou seu limite de aulas.
                    #Caso tenha ultrapassado, verifica se alguma das atividades já atribuídas tem peso menor ou igual ao peso da atividade atual (caso seja igual, o desempate é dado pelo peso 
                    #Da preferência do professor pela matéria), para tentar uma troca, o que altera as variáveis De controle fixed e fixed_activitie, para garantir que haja no máximo uma troca 
                    #por iteração, e para indicar qual atividade seria trocada.
                    for professor in class_professors:
                        subject_professor_weight = subjects_professors.get(professor = professor.professor).professor_weight if subjects_professors.filter(professor = professor.professor).exists() else 1
                        class_professor_weight = class_professors.get(professor = professor.professor).professor_weight if class_professors.filter(professor = professor.professor).exists() else 1
                        highest_subject_professor_weight = subjects_professors.get(professor = chosen_professor).professor_weight if subjects_professors.filter(professor = chosen_professor).exists() else 1
                        highest_class_professor_weight = class_professors.get(professor = chosen_professor).professor_weight if class_professors.filter(professor = chosen_professor).exists() else 11

                        fixed = 0
                        fixed_activitie = None
                        weight = class_professor_weight + subject_professor_weight
                        
                        current_activities = Activitie.objects.filter(tprofessor = professor.professor).order_by("professor_weight")

                        if current_activities and fixed == 0 and professor.professor.num_uses + activitie.activities_qtd > ambient.max_actv_in_cicle:
                            for fix_activitie in current_activities:
                                fixed_subject_professor_weight = fix_activitie.tsubject.favorite_professors.get(professor = fix_activitie.tprofessor).professor_weight if fix_activitie.tsubject.favorite_professors.filter(professor = fix_activitie.tprofessor).exists() else 1
                                fixed_class_professor_weight = fix_activitie.tclass.favorite_professors.get(professor = fix_activitie.tprofessor).professor_weight if fix_activitie.tclass.favorite_professors.filter(professor = fix_activitie.tprofessor).exists() else 1

                                if (professor.professor.num_uses - fix_activitie.activities_qtd + activitie.activities_qtd) <= ambient.max_actv_in_cicle:
                                    if (fix_activitie.professor_weight < weight and ((fixed_subject_professor_weight < 100 and fixed_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                        fixed = 1
                                        fixed_activitie = fix_activitie
                                        break
                                    elif (fix_activitie.professor_weight == weight and ((fixed_subject_professor_weight < 100 and fixed_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                        try:
                                            preference1 = professor.professor.prefered_subjects.get(subject = activitie.tsubject).subject_weight
                                        except Subject_Preference.DoesNotExist:
                                            preference1 = 0
                                        try:
                                            preference2 = professor.professor.prefered_subjects.get(subject = fix_activitie.tsubject).subject_weight
                                        except Subject_Preference.DoesNotExist:
                                            preference2 = 0

                                        if preference1 > preference2:
                                            fixed = 1
                                            fixed_activitie = fix_activitie
                                        break
                                    else:
                                        break
                        
                        #Agora, o algoritmo inicia a etapa de comparação dos pesos para escolher o professor, considerando dois casos diferentes
                        #fixed == 0, o que significa que não houve uma troca, logo, a variável de controle swap permanece 0 e swap_activitie None, para garantir que nenhuma troca será feita na atribuição definitiva
                        #fixed == 1, houve uma troca, então, além de pré-atribuir o professor, as variáveis de controle são alteradas para garantir que a atividade seja trocada a atribuição definitiva.
                        #Em cada uma delas, o processo é basicamente o mesmo, se o peso atual for maior que o maior peso, o professor é pré-selecionado como escolhido, se for igual, os critérios de desempate são aplicados.
                        #A única diferença é o estado das variáveis de controle após a escolha.
                        if fixed == 0 and ((professor.professor.num_uses + activitie.activities_qtd <= ambient.max_actv_in_cicle) or (professor.professor_weight == 100 or subject_professor_weight == 100)):
                            timetable = list(ambient.published_timetable.table.all())
                            activities_with_professor = list(ambient.activities.filter(tprofessor = professor.professor))
                            activities_with_professor.append(activitie)

                            conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, professor)

                            if conflitant_schedules:
                                if (weight > highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    if subjects_professors.filter(professor = professor.professor):
                                        subject_professor_weight = subjects_professors.get(professor = professor.professor)
                                    if(professor.professor_weight != 0 and subject_professor_weight != 0):
                                        chosen_professor = professor.professor
                                        highest_weight = weight
                                        swap = 0
                                        swapAct = None
                                        chosen_conflitant_professor = conflitant_schedules
                                elif (weight == highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    tchosen_professor = tiebreaker(professor.professor, chosen_professor, activitie)[0]
                                    if tchosen_professor == professor.professor:
                                        swap = 0
                                        swapAct = None
                                        chosen_professor = professor.professor
                                        highest_weight = weight
                                        chosen_conflitant_professor = conflitant_schedules
                        elif fixed == 1:
                            timetable = list(ambient.published_timetable.table.all())
                            activities_with_professor = list(ambient.activities.filter(tprofessor = professor.professor))
                            activities_with_professor.append(activitie)

                            conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, professor)
                            
                            if conflitant_schedules:
                                if (weight > highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    if(professor.professor_weight != 0 and subject_professor_weight != 0):
                                        highest_weight = weight
                                        chosen_professor = professor.professor
                                        swap = 1
                                        swapAct = fixed_activitie
                                        chosen_conflitant_professor = conflitant_schedules
                                elif (weight == highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    tchosen_professor = tiebreaker(professor.professor, chosen_professor, activitie)[0]
                                    if tchosen_professor == professor.professor:
                                        swap = 1
                                        swapAct = fixed_activitie
                                        chosen_professor = professor.professor
                                        highest_weight = weight
                                        chosen_conflitant_professor = conflitant_schedules
                            fixed = 0

                    #Agora, o processo é repetido, mas levando em conta apenas as preferências da matéria. Isso é importante para os casos em que não há preferência por parte da disciplina,
                    #Mas há por parte da materia.
                    for professor in subjects_professors:
                        subject_professor_weight = subjects_professors.get(professor = professor.professor).professor_weight if subjects_professors.filter(professor = professor.professor).exists() else 1
                        class_professor_weight = class_professors.get(professor = professor.professor).professor_weight if class_professors.filter(professor = professor.professor).exists() else 1
                        highest_subject_professor_weight = subjects_professors.get(professor = chosen_professor).professor_weight if subjects_professors.filter(professor = chosen_professor).exists() else 1
                        highest_class_professor_weight = class_professors.get(professor = chosen_professor).professor_weight if class_professors.filter(professor = chosen_professor).exists() else 1
                        
                        fixed = 0
                        weight = subject_professor_weight
                        current_activities = Activitie.objects.filter(tprofessor = professor.professor).order_by("-professor_weight")
                        if current_activities and fixed == 0:
                            for fix_activitie in current_activities:
                                if (professor.professor.num_uses - fix_activitie.activities_qtd + activitie.activities_qtd) <= ambient.max_actv_in_cicle and professor.professor.num_uses + activitie.activities_qtd > ambient.max_actv_in_cicle:    
                                    
                                    if fix_activitie.professor_weight < weight:
                                        fixed = 1
                                    elif fix_activitie.professor_weight == weight:
                                        try:
                                            preference1 = professor.professor.prefered_subjects.get(subject = activitie.tsubject).subject_weight
                                        except Subject_Preference.DoesNotExist:
                                            preference1 = 0
                                        try:
                                            preference2 = professor.professor.prefered_subjects.get(subject = fix_activitie.tsubject).subject_weight
                                        except Subject_Preference.DoesNotExist:
                                            preference2 = 0
                                        if preference1 > preference2:
                                            fixed = 1

                        if fixed == 0 and (professor.professor.num_uses + activitie.activities_qtd <= ambient.max_actv_in_cicle) or (professor.professor_weight == 100):
                            timetable = list(ambient.published_timetable.table.all())
                            activities_with_professor = list(ambient.activities.filter(tprofessor = professor.professor))
                            activities_with_professor.append(activitie)

                            conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, professor.professor)
                            if conflitant_schedules:
                                if (weight > highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    highest_weight = weight
                                    chosen_professor = professor.professor
                                    swap = 0
                                    swapAct = None
                                    chosen_conflitant_professor = conflitant_schedules
                                elif (weight == highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    tchosen_professor = tiebreaker(professor.professor, chosen_professor, activitie)[0]
                                    if tchosen_professor == professor.professor:
                                        swap = 0
                                        swapAct = None
                                        chosen_professor = professor.professor
                                        highest_weight = weight
                                        chosen_conflitant_professor = conflitant_schedules
                        elif fixed == 1:
                            timetable = list(ambient.published_timetable.table.all())
                            activities_with_professor = list(ambient.activities.filter(tprofessor = professor.professor))
                            activities_with_professor.append(activitie)

                            conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, professor)

                            if conflitant_schedules and not isinstance(conflitant_schedules, Activitie):
                                if (weight > highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    if(professor.professor_weight != 0):
                                        highest_weight = weight
                                        chosen_professor = professor.professor
                                        swap = 1
                                        swapAct = fixed_activitie
                                        chosen_conflitant_professor = conflitant_schedules
                                elif (weight == highest_weight and ((highest_subject_professor_weight < 100 and highest_class_professor_weight < 100) or (subject_professor_weight >= 100 or class_professor_weight >= 100))):
                                    tchosen_professor = tiebreaker(professor.professor, chosen_professor, activitie)[0]
                                    if tchosen_professor == professor.professor:
                                        swap = 1
                                        swapAct = fixed_activitie
                                        chosen_professor = professor.professor
                                        highest_weight = weight
                                        chosen_conflitant_professor = conflitant_schedules
                            fixed = 0
                    
                    #Aqui é feita a atribuição definitiva do professor escolhido, verificando se há conflitos
                    if(highest_weight > 0 and chosen_professor != None):
                        activitie.tprofessor = chosen_professor
                        activitie.professor_weight = highest_weight
                        activitie.save()
                        chosen_professor.num_uses += activitie.activities_qtd
                        if swap:
                            swapAct.tprofessor = None
                            swapAct.professor_weight = 0
                            swapAct.save()
                            swapAct.tprofessor.num_uses -= swapAct.activities_qtd
                            repeat = True
                        if isinstance(chosen_conflitant_professor, Activitie):
                            tprofessor = chosen_conflitant_professor.tprofessor
                            tprofessor.num_uses -= chosen_conflitant_professor.activities_qtd
                            tprofessor.save()
                            chosen_conflitant_professor.tprofessor = None   
                            chosen_conflitant_professor.professor_weight = 0
                            chosen_conflitant_professor.save()
                            repeat = True

            
            #Agora que foi atribuido com base nas preferências da classe e da matéria, vai começar a atribuição com base nas preferências de matéria do professor 
            #O algoritmo seleciona por materia, depois filtra os professores que têm preferência por ela, ordenando por peso da preferência e número de usos do professor.
            subjects = ambient.subjects.all()
            count = 0
            repeat = True
            #Este while se repe no máximo dez vezes, enquanto houverem trocas de atividade que deixem uma atividade sem professor, dando a chance de fazer uma nova atribuição para esta atividade
            while count < 10 and repeat == True:
                count += 1
                repeat = False
                for subject in subjects:
                    relevant_professors = ambient.members.all().filter(is_professor = True, prefered_subjects__subject = subject).order_by("-prefered_subjects__subject_weight", "num_uses")
                    subject_preference = 1
                    selected = 1
                    activities_with_subject = ambient.activities.all().filter(tsubject = subject, tprofessor = None)

                    #O algoritmo se repete enquando houverem matérias sem professores, professores que querem essa matéria (os professores são excluídos da lista quando não 
                    #puderem mais ser utilizados) e ao menos um professor for selecionado para a tentativa de utilização.
                    while(ambient.activities.all().filter(tsubject = subject, tprofessor = None) and relevant_professors and selected != 0):
                        highest_weight = 0
                        chosen_professor = None
                        chosen_conflitant_professor = None
                        #O algoritmo itera sobre os professores relevantes para a matéria, comparando pelo peso da preferência do professor pela matéria e aplicando os 
                        # critérios de desempate se necessário, selecionando um professor para tentar atribuir.
                        for professor in relevant_professors:
                            professor_subject = professor.prefered_subjects.get(subject = subject)
                            weight = professor_subject.subject_weight

                            
                            if professor_subject.subject_weight > highest_weight:
                                if(subject.favorite_professors.all().filter(professor = professor)):
                                    subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                if subject_preference != 0:
                                    chosen_professor = professor
                                    highest_weight = professor_subject.subject_weight
                            elif professor_subject.subject_weight == highest_weight:
                                tchosen_professor = tiebreaker(professor, chosen_professor, activitie)[0]
                                if tchosen_professor == professor:
                                    chosen_professor = professor
                                    highest_weight = professor_subject.subject_weight

                        #Se houver um professor escolhido, o algoritmo organiza as atividades disponíveis ordenando com base na quantidade de horários preferidos coincidentes
                        #Com o professor. Para cada atividade, verifica se é possível atribuir dado o número de usos do professor, se for possível, ele fará a verificação de sempre
                        #e atribuirá a atividade ao professor, ou, caso haja um professor já atribuído, fará a comparação de pesos e critérios de desempate para decidir se troca ou 
                        #não o professor da atividade. Caso o professor ultrapasse o número de usos com a atribuição da atividade, são analisadas todas as suas atividades atuais. Caso 
                        #uma delas permita a atribuição da nova atividade se tiver o número de usos subtraído e tenha peso menor que a preferência do professor pela matéria, as verificações 
                        #são realizadas, e a nova atividade pode ser atribuída ao professor. A atividade anteriormente atribuída a ele, por sua vez, passará a ser tratada como uma 
                        #atividade sem professor.
                        if chosen_professor:
                            activities_with_subject = sorted(activities_with_subject, key=lambda subject_activitie: (sum(1 for schedule in subject_activitie.tclass.prefered_schedules.all() if chosen_professor.prefered_schedules.filter(id=schedule.id))), reverse=True)
                            current_activities = Activitie.objects.filter(tprofessor = chosen_professor).order_by("professor_weight")
                            professor_subject = chosen_professor.prefered_subjects.get(subject = subject)
                            used = 0
                            for subject_activitie in activities_with_subject:
                                if (chosen_professor.num_uses + subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods <= ambient.max_actv_in_cicle):
                                    subject_preference = 1
                                    class_preference = 1
                                    
                                    if not(subject_activitie.tprofessor):
                                        if subject_activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                            subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                        if subject_activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                            class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                        if subject_preference != 0 and class_preference != 0:
                                            timetable = list(ambient.published_timetable.table.all())
                                            activities_with_professor = list(ambient.activities.filter(tprofessor = chosen_professor))
                                            activities_with_professor.append(subject_activitie)
                                            
                                            conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, chosen_professor)

                                            if conflitant_schedules:
                                                tactv = ambient.activities.get(id = subject_activitie.id)
                                                tactv.tprofessor = chosen_professor
                                                tactv.professor_weight = professor_subject.subject_weight
                                                tactv.save()
                                                chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                chosen_professor.save()
                                                used = 1
                                                if isinstance(conflitant_schedules, Activitie):
                                                    conflitant_professor = conflitant_schedules.tprofessor
                                                    conflitant_schedules.tprofessor = None
                                                    conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                    conflitant_schedules.save()
                                                    conflitant_professor.save()
                                                    repeat = True
                                                    
                                    else:
                                        tchosen_professor = tiebreaker(chosen_professor, subject_activitie.tprofessor, subject_activitie)[0]
                                        if tchosen_professor == chosen_professor:
                                            if subject_activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                                subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                            if subject_activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                                class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                            if subject_preference != 0 and class_preference != 0:
                                                timetable = list(ambient.published_timetable.table.all())
                                                activities_with_professor = list(ambient.activities.filter(tprofessor = chosen_professor))
                                                activities_with_professor.append(subject_activitie)
                                                conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, chosen_professor)

                                                if conflitant_schedules:
                                                    subject_activitie.tprofessor = chosen_professor
                                                    subject_activitie.professor_weight = professor_subject.subject_weight
                                                    subject_activitie.save()
                                                    chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                    subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                    subject_activitie.tprofessor.save()
                                                    chosen_professor.save()
                                                    used = 1
                                                    if isinstance(conflitant_schedules, Activitie): #tem que trocar isso aqui pelo chosen_conflitant_professor
                                                        conflitant_professor = conflitant_schedules.tprofessor
                                                        conflitant_schedules.tprofessor = None
                                                        conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                        conflitant_schedules.save()
                                                        conflitant_professor.save()
                                                        repeat = True
                                else:
                                    for c_activitie in current_activities:
                                        if c_activitie.professor_weight < professor_subject.subject_weight:
                                            if(chosen_professor.num_uses - c_activitie.tclass.activities_qtd + subject_activitie.tclass.activities_qtd <= ambient.max_actv_in_cicle):
                                                subject_preference = 1
                                                class_preference = 1
                                                
                                                if not(subject_activitie.tprofessor):
                                                    if subject_activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                                        subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                                    if subject_activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                                        class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                                    if subject_preference != 0 and class_preference != 0:
                                                        timetable = list(ambient.published_timetable.table.all())
                                                        activities_with_professor = list(ambient.activities.filter(tprofessor = chosen_professor))
                                                        activities_with_professor.append(subject_activitie)
                                                        
                                                        conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, chosen_professor)

                                                        if conflitant_schedules and not isinstance(conflitant_schedules, Activitie):
                                                            c_activitie.tprofessor = None
                                                            c_activitie.professor_weight = 0
                                                            c_activitie.save()
                                                            tactv = ambient.activities.get(id = subject_activitie.id)
                                                            tactv.tprofessor = chosen_professor
                                                            tactv.professor_weight = professor_subject.subject_weight
                                                            tactv.save()
                                                            chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                            chosen_professor.save()
                                                            used = 1
                                                            repeat = True
                                                else:
                                                    tchosen_professor = tiebreaker(chosen_professor, subject_activitie.tprofessor, subject_activitie)[0]
                                                    if tchosen_professor == chosen_professor:
                                                        if subject_activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                                            subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                                        if subject_activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                                            class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                                        if subject_preference != 0 and class_preference != 0:
                                                            timetable = list(ambient.published_timetable.table.all())
                                                            activities_with_professor = list(ambient.activities.filter(tprofessor = chosen_professor))
                                                            activities_with_professor.append(subject_activitie)
                                                            conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, chosen_professor)

                                                            if conflitant_schedules and not isinstance(conflitant_schedules, Activitie):
                                                                c_activitie.tprofessor = None
                                                                c_activitie.professor_weight = 0
                                                                c_activitie.save()
                                                                subject_activitie.tprofessor = chosen_professor
                                                                subject_activitie.professor_weight = professor_subject.subject_weight
                                                                subject_activitie.save()
                                                                chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                subject_activitie.tprofessor.save()
                                                                chosen_professor.save()
                                                                used = 1
                                                                repeat = True

                        #Se, ao chegar ao fim, a variável de controle user permanecer a mesma, significa que ele não foi atribuido a nenhuma atividade, portanto deve
                        #ser retirado da lista. Se nenhum professor for selecionado em chosen_professor, a variável selected é alterada para 0, e dessa forma, o loop acaba.
                            if used == 0:
                                relevant_professors = relevant_professors.exclude(id=chosen_professor.id)
                        else: selected = 0
            
            #Agora, as aulas ainda sem professor serão atribuídas a professores que tenham as formações que sejam interessantes para a disciplina. Selecionando-as e ordenando-as do maior para o menor peso.
            #O algoritmo itera sobre as atividades, e para cada atividade, itera sobre suas preferências de formação, buscando professores que têm aquela formação, comparando seus pesos e
            #Aplicando critérios para escolher o melhor.
            count = 0
            repeat = True
            #Este while se repe no máximo dez vezes, enquanto houverem trocas de atividade que deixem uma atividade sem professor, dando a chance de fazer uma nova atribuição para esta atividade
            while count < 10 and repeat == True:
                count += 1
                repeat = False
                not_atribuited_activities = ambient.activities.all().filter(tprofessor = None)
                for not_atribuited_activitie in not_atribuited_activities:
                    formations = not_atribuited_activitie.tsubject.relevant_formations.all().order_by("-formation_weight")
                    chosen_professor = None
                    highest_weight = 0
                    chosen_conflitant_schedules = None
                    for formation in formations:
                        weight = not_atribuited_activitie.tsubject.relevant_formations.get(formation = formation.formation).formation_weight
                        candidates = ambient.members.filter(is_professor = True, formations__formation = formation.formation).order_by('num_uses')
                        for candidate in candidates:
                            subject_preference = 1
                            class_preference = 1
                            if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = candidate):
                                subject_preference = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = candidate).professor_weight
                            if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = candidate):
                                class_preference = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = candidate).professor_weight
                            #Verifica se o candidato atende aos requisitos (pesos diferentes de 0 e disponibilidade horária). Se não houver professor alocado, ele é imediatamente selecionado
                            #Se houver, os critérios de desempate são aplicados, e o que vencer, permanece. Após verificar se há conflitos, o professor é pré-atribuído.
                            if subject_preference != 0 and class_preference != 0 and weight > highest_weight and candidate.num_uses + not_atribuited_activitie.tclass.necessary_subjects.get(subject = not_atribuited_activitie.tsubject).periods <= ambient.max_actv_in_cicle:
                                if chosen_professor:
                                    tchosen_professor = tiebreaker(candidate, chosen_professor, not_atribuited_activitie)[0]
                                else:
                                    tchosen_professor = candidate

                                if tchosen_professor == candidate:
                                    timetable = list(ambient.published_timetable.table.all())
                                    activities_with_professor = list(ambient.activities.filter(tprofessor = tchosen_professor))
                                    activities_with_professor.append(not_atribuited_activitie)
                                    conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, tchosen_professor)

                                    if conflitant_schedules:
                                        chosen_conflitant_schedules = conflitant_schedules
                                        chosen_professor = candidate
                                        highest_weight = weight
                    #Atribuição definitiva.      
                    if chosen_professor:
                        not_atribuited_activitie.tprofessor = chosen_professor
                        not_atribuited_activitie.professor_weight = highest_weight
                        not_atribuited_activitie.save()
                        chosen_professor.num_uses += not_atribuited_activitie.activities_qtd
                        chosen_professor.save()
                        if isinstance(chosen_conflitant_schedules, Activitie):
                            conflitant_professor = chosen_conflitant_schedules.tprofessor
                            chosen_conflitant_schedules.tprofessor = None
                            conflitant_professor.num_uses -= chosen_conflitant_schedules.activities_qtd
                            chosen_conflitant_schedules.save()
                            conflitant_professor.save()
                            repeat = True
   
            #Se ainda assim houverem atividades sem professor, elas serão atribuídas randomicamente a professores que tenham menos uso (deve gerar um aviso nessas atividades).

            not_atribuited_activities = ambient.activities.all().filter(tprofessor = None)
            
            for not_atribuited_activitie in not_atribuited_activities:
                candidates = ambient.members.all().filter(is_professor = True).order_by('num_uses')
                chosen_professor = None
                for candidate in candidates:
                    subject_preference = 1
                    class_preference = 1
                    if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = candidate):
                        subject_preference = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = candidate).professor_weight
                    if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = candidate):
                        class_preference = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = candidate).professor_weight

                    timetable = list(ambient.published_timetable.table.all())
                    activities_with_professor = list(ambient.activities.filter(tprofessor = candidate))
                    activities_with_professor.append(not_atribuited_activitie)
                    conflitant_schedules = check_conflitant_schedules_professor(activities_with_professor, timetable, candidate)

                    if subject_preference != 0 and class_preference != 0 and candidate.num_uses + not_atribuited_activitie.activities_qtd <= ambient.max_actv_in_cicle and conflitant_schedules:          
                        chosen_professor = candidate
                        chosen_conflitant_schedules = conflitant_schedules
                        break

                if chosen_professor:
                    not_atribuited_activitie.tprofessor = chosen_professor
                    not_atribuited_activitie.professor_weight = highest_weight
                    chosen_professor.num_uses += not_atribuited_activitie.activities_qtd
                    not_atribuited_activitie.save()
                    chosen_professor.save()

            return redirect(f'/ambient/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

#Este é um algoritmo clássico de agendamento, ele utiliza de backtraging para alocar as atividades, testando cada possibilidade de horário para cada atividade, e, caso 
#haja mais de uma atividade, ele chama a si mesmo para alocar a próxima atividade. Caso haja um conflito, ele volta e testa a próxima possibilidade de horário da 
#atividade anterior. Se chegar ao fim das possibilidades de horário desta, ele volta para a atividade anterior e testa a próxima possibilidade de horário dela, e assim 
#por diante. Se chegar ao fim das possibilidades de horário da primeira atividade, significa que não há solução possível para aquela ordem de atividades.
def alocate(ambient, timetable, activities):
    #seleciona a primeira atividade, que será alocada no momento
    activitie = activities[0]
    
    #Obtém os horários preferidos do professor para priorizar aqueles que também são preferidos da turma
    professor_preferred_schedules = set()
    if activitie.tprofessor and hasattr(activitie.tprofessor, 'prefered_schedules'):
        for schedule in activitie.tprofessor.prefered_schedules.all():
            professor_preferred_schedules.add((schedule.line, schedule.column))
    
    #Ordena os horários preferidos da turma: primeiro os que também são preferidos do professor
    class_schedules = list(activitie.tclass.prefered_schedules.all())
    class_schedules.sort(key=lambda s: (s.line, s.column) not in professor_preferred_schedules)
    
    for start in class_schedules:
        available = True
        fixed_timetable = {key: value.copy() for key, value in timetable.items()}
        #Define o início da atividade com start, o ponto de onde a alocação irá partir, pré-define como disponível e cria uma cópia da grade horária para não alterar a original
        #caso seja necessário voltar atrás e usá-la como estava antes
        
        #Tenta, a partir do ponto de início, alocar a atividade com todos os períodos necessários, somando uma linha a cada período e verificando se naquele slot, existe 
        #um array [] vazio ou com outras atividades. Se houver, verifica se uma delas tem a mesma sala, professor ou classe da atividade que se quer alocar, o que significaria 
        #um conflito e, portanto, define o status de available como false.
        for i in range(activitie.activities_qtd):
            try:
                key = (start.line + i, start.column)
                slot = fixed_timetable[key]
            except:
                slot = None
            if slot == [] or slot:
                available = True
                for act in slot:
                    if act.tclass == activitie.tclass or act.tprofessor == activitie.tprofessor or act.tclassroom == activitie.tclassroom:
                        available = False
                        break
            else:
                available = False
                break
        
        #Se o horário estiver disponível, a atividade é adicionada aos slots no dicionário, para que as outras atividades também saibam que ela está ali, e uma nova função é
        #chamada caso o tamanho de atividades seja maior que 1, indicando que ainda há atividades para serem atribuidas, incluindo o estado atual do dicionário com todas 
        #as atividades já alocadas e as atividades restantes, Se o tamanho da atividades for igual a 1, significa que o algorimo chegou ao fim, então ele retorna o dicionário 
        #final para ser alocado na grade horária do ambiente. Caso algo aconteça de errado e uma atividade não possa ser alocada em nenhum horário, ela retorna falso e o 
        #processo reinicia de onde parou.
        if available:
            for i in range(activitie.activities_qtd):
                key = (start.line + i, start.column)
                fixed_timetable[key].append(activitie)

            if len(activities) > 1:
                check = alocate(ambient, fixed_timetable, activities[1:])
                if check:
                    return check
            else:
                return fixed_timetable
    return False


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
        
        if ambient.members.filter(user = user) and member.admin_type.can_run_alocation:
            #O algoritmo inicia criando uma tabela vazia, que será preenchida em breve
            timetable = Timetable(lines_number = ambient.periods_in_a_day, columns_number = ambient.days_in_a_cicle)
            timetable.save()
            ambient.published_timetable = timetable
            ambient.save()
            for schedule in ambient.available_schedules.all():
                alocation = Alocation(line = schedule.line, column = schedule.column)
                alocation.save()
                ambient.published_timetable.table.add(alocation)
                ambient.save()

            #Agora, cria o dicionário com todos os horários e organiza as funções de acordo com a menor quandidade de horários preferidos e maior quantidade de períodos,
            #para otimizar a execução do algoritmo de alocação
            activities = list(ambient.activities.all())
            fixed_timetable = {}
            for time in timetable.table.all():
                fixed_timetable[(time.line, time.column)] = []
            activities.sort(key=lambda x: (x.tclass.prefered_schedules.count(), -x.activities_qtd))

            #A função é chamada, o dicionário é criado e a grade horária do ambiente é definida
            tdict = alocate(ambient, fixed_timetable, activities)
            if tdict:
                for key, value in tdict.items():
                    alocation = ambient.published_timetable.table.all().get(line = key[0], column = key[1])
                    for act in value:
                        alocation.activitie.add(act)
                        alocation.save()

            #As atividades que não puderam ser alocadas são adicionadas a uma lista, e serão exibidas na tela para o usuário        
            activities = ambient.activities.all()
            not_alocated_activities = []
            for activitie in activities:
                if not ambient.published_timetable.table.all().filter(activitie = activitie):
                    not_alocated_activities.append(activitie)
            for n_activitie in not_alocated_activities:
                un_activitie = Unregistered_Activitie(activitie = n_activitie)
                un_activitie.save()
                ambient.published_timetable.not_alocated.add(un_activitie)
        return redirect(f'/ambient/{ambientid}')
    else:
        return redirect('/')