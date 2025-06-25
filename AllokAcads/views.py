from django.shortcuts import render, redirect
from django.conf import settings
import random, os, datetime, time
from .models import User, Ambient, Member, AdminTP, ClassroomTP, Formation, Subject, Formation_Preference, Classroom, Class, Professor_Preference, Classroom_Preference, Schedule_Preference, Class_Preference, Subject_Preference, Member_Formation, Activitie, Timetable, Alocation, Unregistered_Activitie
from shutil import copyfile
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import logout as logoutauth
from django.contrib.auth import login as loginauth
from django.contrib.auth.models import User as UserAuth

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
        identificator = request.POST.get('id')
        password = request.POST.get('password')
        userauth = authenticate(request, username=identificator, password=password)
        if userauth is not None:
            loginauth(request, userauth)   
            return redirect(f'/home')
        
        return redirect('/?error=login_failed')

def register(request):
    if request.user.is_authenticated:
        return redirect(f'/home')
    else:
        return render(request, "AllokAcads/register.html")

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
    
        while(True):
            identificator = generate_userid()
            user = User.objects.filter(userid = identificator)
            if(len(user) == 0):
                break
            
        directory = os.path.join(settings.BASE_DIR, f'media/users/{identificator}/user_picture')
        os.makedirs(directory, exist_ok=True)
        default_picture_path = os.path.join(settings.BASE_DIR, 'media', 'users/user.png')
        copyfile(default_picture_path, os.path.join(directory, 'user.png'))
        picture = f'users/{identificator}/user_picture/user.png'

        userauth = UserAuth(username=identificator, email=email)
        userauth.set_password(password)
        userauth.save()

        user = User(userid=identificator, picture=picture, name=name, email=email, birthdate=birthdate)
        user.save()

        # Redirecionar para login com dados do usuário na URL (encoded)
        import urllib.parse
        from datetime import datetime
        
        # Converter a data para formato brasileiro se existir
        formatted_birthdate = ''
        if birthdate:
            try:
                # birthdate vem como string "YYYY-MM-DD" do formulário
                date_obj = datetime.strptime(birthdate, '%Y-%m-%d')
                formatted_birthdate = date_obj.strftime('%d/%m/%Y')
            except:
                formatted_birthdate = birthdate
        
        user_data = {
            'userid': identificator,
            'name': name,
            'email': email,
            'birthdate': formatted_birthdate
        }
        encoded_data = urllib.parse.urlencode(user_data)
        return redirect(f'/?new_user=true&{encoded_data}')

def home(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambients = user.ambients.all()
        username = user.name
    
        return render(request, "AllokAcads/home.html", {'user' : user, 'username' : username, 'userid' : userid, 'ambients' : ambients})
    else:
        return redirect('/')

def create_ambient(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
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
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        picture = request.FILES.get('picture')

        name = request.POST.get('name')
        description = request.POST.get('description')

        while(True):
            identificator = generate_ambientid()
            ambient = Ambient.objects.filter(ambientid = identificator)
            if(len(ambient) == 0):
                break

        if not picture: 
            directory = os.path.join(settings.BASE_DIR, f'media/ambients/{identificator}/ambient_picture')
            os.makedirs(directory, exist_ok=True)
            default_picture_path = os.path.join(settings.BASE_DIR, 'media', 'ambients/ambient.png')
            copyfile(default_picture_path, os.path.join(directory, 'ambient.png'))
            picture = f'ambients/{identificator}/ambient_picture/ambient.png'
        
        main_adm = AdminTP(name='Administrador Principal', can_configure_ambient=True, can_gerenciate_members=True, can_register_resources=True, can_run_atribuition=True, can_run_alocation=True)
        main_adm.save()

        creator = Member(user=user, admin_type=main_adm, is_professor=False)

        if not picture:
            directory = os.path.join(settings.BASE_DIR, f'media/ambients/{identificator}/ambient_picture')
            os.makedirs(directory, exist_ok=True)
            default_picture_path = os.path.join(settings.BASE_DIR, 'media', 'ambients/ambient.png')
            copyfile(default_picture_path, os.path.join(directory, 'ambient.png'))
            picture = f'ambients/{identificator}/ambient_picture/ambient.png'

        ambient = Ambient(ambientid=identificator, name=name, picture=picture, description=description)

        user.save()
        ambient.save()
        creator.save()

        user.ambients.add(ambient)
        ambient.admin_types.add(main_adm)
        ambient.members.add(creator)

        return redirect(f'/home')
    else:
        return redirect('/')

def ambient(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid=ambientid).first()
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

            member = ambient.members.filter(user=user).first()
            schedules = ambient.available_schedules.all()
            classrooms = ambient.classrooms.all()
            classes = ambient.classes.all()
            subjects = ambient.subjects.all()
            columns = ambient.periods_in_a_day
            activities = ambient.activities.all()
            picture = ambient.picture
            username = user.name
            
            
            return render(request, "AllokAcads/ambient.html", {
                'ambient': ambient,
                'user': user,
                'userid': userid,
                'username': username,
                'member': member,
                'schedules': schedules,
                'classrooms': classrooms,
                'classes': classes,
                'subjects': subjects,
                'columns': columns,
                'picture': picture,
                'activities': activities,
                'table': ordered_table,
                'not_alocated': not_alocated
            })
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_form(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid=ambientid).first()
        if ambient.members.filter(user = user): 
            member = ambient.members.filter(user=user).first()
            schedules = ambient.available_schedules.all()
            classrooms = ambient.classrooms.all()
            classes = ambient.classes.all()
            subjects = ambient.subjects.all()
            columns = ambient.periods_in_a_day
            activities = ambient.activities.all()
            picture = ambient.picture
            username = user.name

            return render(request, "AllokAcads/ambient_form.html", {
                'ambient': ambient,
                'user': user,
                'userid': userid,
                'username': username,
                'member': member,
                'schedules': schedules,
                'classrooms': classrooms,
                'classes': classes,
                'subjects': subjects,
                'columns': columns,
                'picture': picture,
                'activities': activities,
            })
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_config(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid=ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_configure_ambient:  
            member = member[0]
            
            context = {
                'ambient': ambient[0],
                'user': user,
                'userid': userid, 
                'member': member
            }
            
            return render(request, "AllokAcads/ambient_config.html", context)
        else:
            return redirect('home')
    else:
        return redirect('/')


def ambient_config_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_configure_ambient:  
            ambient_instance = Ambient.objects.get(ambientid = ambientid)

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

            if picture:
                picture_path = ambient_instance.picture.path
                ambient_instance.picture = picture
                os.remove(picture_path)
            if name:
                ambient_instance.name = name
            if description:
                ambient_instance.description = description
            if periods_in_a_day:
                ambient_instance.periods_in_a_day = periods_in_a_day
            if days_in_a_cicle:
                ambient_instance.days_in_a_cicle = days_in_a_cicle
            
            ambient_instance.form_opening = form_opening if form_opening else None
            ambient_instance.form_closing = form_closing if form_closing else None
            ambient_instance.alt_solicitations_opening = alt_solicitations_opening if alt_solicitations_opening else None
            ambient_instance.alt_solicitations_closing = alt_solicitations_closing if alt_solicitations_closing else None
            
            if min_actv_in_a_day:
                ambient_instance.min_actv_in_day = min_actv_in_a_day
            if max_actv_in_a_day:
                ambient_instance.max_actv_in_day = max_actv_in_a_day
            if min_actv_in_a_cicle:
                ambient_instance.min_actv_in_cicle = min_actv_in_a_cicle
            if max_actv_in_a_cicle:
                ambient_instance.max_actv_in_cicle = max_actv_in_a_cicle

            ambient_instance.save()

            if (periods_in_a_day and days_in_a_cicle) or (periods_in_a_day and ambient_instance.days_in_a_cicle) or (ambient_instance.periods_in_a_day or days_in_a_cicle):
                ambient_instance.available_schedules.all().delete()
                for i in range(int(days_in_a_cicle)):
                    for j in range(int(periods_in_a_day)):
                        schedule = Schedule_Preference(line=i, column=j)
                        schedule.save()
                        ambient_instance.available_schedules.add(schedule)

            messages.success(request, 'Configurações do ambiente atualizadas com sucesso!')
            return redirect(f'/ambient/config/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_profile(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.get(ambientid = ambientid)
        if ambient.members.filter(user = user):      
            picture = user.picture
            return render(request, "AllokAcads/ambient_profile.html", {'user' : user, 'ambient' : ambient, 'picture' : picture, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_members(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        if ambient[0].members.filter(user = user):         
            members = ambient[0].members.all()
            member = ambient[0].members.get(user = user)
            return render(request, "AllokAcads/ambient_members.html", {'ambient' : ambient[0], 'user' : user, 'members' : members,  'tmember' : member, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_form_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].is_professor:   
            available_schedules = request.POST.getlist('available_schedules')
            prefered_subjects = request.POST.getlist('prefered_subjects')
            if available_schedules:
                for available_schedule in available_schedules:
                    schedule = Schedule_Preference.objects.get(id = available_schedule)
                    member[0].prefered_schedules.add(schedule)
            for prefered_subject in prefered_subjects:
                subject = Subject.objects.get(id = prefered_subject)
                subject_weight = int(request.POST.get(f"option_{prefered_subject}"))
                subject_preference = Subject_Preference(subject=subject, subject_weight=subject_weight)
                subject_preference.save()
                member[0].prefered_subjects.add(subject_preference)
            return redirect(f'/ambient/form/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_solicitations(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_gerenciate_members:
            solicitations = ambient.enter_solicitations
            names = []
            for solicitation in solicitations:
                name = User.objects.get(userid = solicitation).name
                names.append(name)
            solicitations = zip(names, solicitations)
            solicitations_list = list(zip(names, solicitations))
            return render(request, "AllokAcads/ambient_solicitations.html", {'solicitations' : solicitations, 'solicitations_list' : solicitations_list, 'ambient' : ambient, 'user' : user, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def accept_solicitation(request, memberid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:  
            member = User.objects.get(userid = memberid)
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
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:  
            ambient.enter_solicitations.remove(memberid)
            return redirect(f'/ambient/solicitations{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_resources(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid=ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
    
            ambient = ambient[0]
            username = user.name    
            context = {
                'ambient': ambient,
                'user': user,
                'userid': userid,
                'username': username 
            }
            
            return render(request, "AllokAcads/ambient_resources.html", context)
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_subjects(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            subjects = ambient[0].subjects.all()
            return render(request, "AllokAcads/ambient_subjects.html", {'ambient' : ambient[0], 'user' : user, 'subjects' : subjects, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_subjects(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            classrooms = ambient[0].classrooms.all()
            professors = ambient[0].members.all().filter(is_professor = True)
            formations = ambient[0].formations.all()
            return render(request, "AllokAcads/ambient_create_subjects.html", {'ambient' : ambient[0], 'user' : user, 'classrooms' : classrooms, 'professors' : professors, 'formations' : formations, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_subjects(request, subjectid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            subject = Subject.objects.get(id = subjectid)
            classrooms = ambient.classrooms.all()
            professors = ambient.members.all().filter(is_professor = True)
            formations = ambient.formations.all()
            return render(request, "AllokAcads/ambient_edit_subjects.html", {'subject': subject, 'ambient': ambient, 'subjectid': subjectid, 'user': user, 'classrooms' : classrooms, 'professors' : professors, 'formations' : formations, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_subjects_validate(request, subjectid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            name = request.POST.get("name")
            subject = Subject.objects.get(id = subjectid)

            classroom_ids = request.POST.getlist("ideal_classrooms")
            professor_ids = request.POST.getlist("favorite_professors")
            formation_ids = request.POST.getlist("relevant_formations")
            
            if name or classroom_ids or professor_ids or formation_ids:
                if name:
                    subject.name = name

                if classroom_ids:
                    subject.ideal_classrooms.clear()
                    for classroom_id in classroom_ids:
                        classroom = Classroom.objects.get(id = classroom_id)
                        classroom_weight = request.POST.get(f"classroom_weight_{classroom_id}")
                        classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
                        classroom_preference.save()
                        subject.ideal_classrooms.add(classroom_preference)
            
                if professor_ids:
                    subject.favorite_professors.clear()
                    for professor_id in professor_ids:
                        professor = Member.objects.get(id = professor_id)
                        professor_weight = request.POST.get(f"professor_weight_{professor_id}")
                        professor_preference = Professor_Preference(professor=professor, professor_weight=professor_weight)
                        professor_preference.save()
                        subject.favorite_professors.add(professor_preference)
                
                if formation_ids:
                    subject.relevant_formations.clear()
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
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            subject = Subject.objects.get(id = subjectid)
            subject.delete()
            return redirect(f'/ambient/resources/subjects/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_classes(request, classid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        tclass = Class.objects.get(id = classid)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            user = User.objects.get(userid = userid)
            schedules = ambient.available_schedules.all()
            classrooms = ambient.classrooms.all()
            professors = ambient.members.all().filter(is_professor = True)
            subjects = ambient.subjects.all()
            columns = ambient.periods_in_a_day
            username = user.name
            return render(request, "AllokAcads/ambient_edit_class.html", {'tclass' : tclass, 'ambient': ambient, 'classid': classid, 'user': user, 'userid': userid, 'username': username, 'classrooms': classrooms, 'professors': professors, 'subjects': subjects, 'schedules': schedules, 'columns': columns})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_classes_validate(request, classid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            name = request.POST.get("name")
            number_of_students = request.POST.get("number_of_students")
            tclass = Class.objects.get(id = classid)
            schedule_ids = request.POST.getlist("available_schedules")
            classroom_ids = request.POST.getlist("ideal_classrooms")
            professor_ids = request.POST.getlist("favorite_professors")
            subject_ids = request.POST.getlist("necessary_subjects")

            if name or number_of_students or schedule_ids or classroom_ids or professor_ids or subject_ids:
                if name:
                    tclass.name = name
                if number_of_students:
                    tclass.number_of_students = number_of_students
                
                if schedule_ids:
                    tclass.prefered_schedules.clear()
                    for schedule_id in schedule_ids:
                        schedule = Schedule_Preference.objects.get(id = schedule_id)
                        tclass.prefered_schedules.add(schedule)
                
                if classroom_ids:
                    tclass.ideal_classrooms.clear()
                    for classroom_id in classroom_ids:
                        classroom = Classroom.objects.get(id = classroom_id)
                        classroom_weight = request.POST.get(f"classroom_weight_{classroom_id}")
                        classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
                        classroom_preference.save()
                        tclass.ideal_classrooms.add(classroom_preference)
                
                if professor_ids:
                    tclass.favorite_professors.clear()
                    for professor_id in professor_ids:
                        professor = Member.objects.get(id = professor_id)
                        professor_weight = request.POST.get(f"professor_weight_{professor_id}")
                        professor_preference = Professor_Preference(professor=professor, professor_weight=professor_weight)
                        professor_preference.save()
                        tclass.favorite_professors.add(professor_preference)
                
                tclass.necessary_subjects.clear()
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
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            member = ambient.members.filter(user = user)
            tclass = Class.objects.get(id = classid)
            tclass.delete()
            return redirect(f'/ambient/resources/classes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_rooms(request, roomid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        room = Classroom.objects.get(id = roomid)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            member = ambient.members.filter(user = user)
            roomtypes = ambient.classroom_types.all()
            return render(request, "AllokAcads/ambient_edit_rooms.html", {'room': room, 'ambient': ambient, 'roomid': roomid, 'user': user, 'roomtypes': roomtypes})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_rooms_validate(request, roomid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            room = Classroom.objects.get(id = roomid)
            name = request.POST.get("name")
            if name:
                room.name = name
            roomtype = request.POST.get("roomtype")
            if roomtype:
                room.classroom_type = ClassroomTP.objects.get(id = request.POST.get('roomtype'))
            capacity = request.POST.get("capacity")
            if capacity:
                room.classroom_capacity = capacity
            if name or capacity or roomtype:
                room.save()
            return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_delete_rooms(request, roomid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            room = Classroom.objects.get(id = roomid)
            room.delete()
            return redirect(f'/ambient/resources/rooms/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_formations(request, formationid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            roomtypes = ambient.classroom_types.all()
            formation = Formation.objects.get(id = formationid)
            return render(request, "AllokAcads/ambient_edit_formations.html", {'formation': formation, 'ambient': ambient, 'formationid': formationid, 'user': user, 'roomtypes': roomtypes})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_formations_validate(request, formationid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        ambient_instance = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            name = request.POST.get('name')    
            formation = Formation.objects.get(id = formationid)
            if name:
                formation.name = name
                formation.save()
                ambient_instance.formations.add(formation)
            return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_delete_formations(request, formationid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            formation = Formation.objects.get(id = formationid)
            formation.delete()
            return redirect(f'/ambient/resources/formations/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_edit_roomtypes(request, roomid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            roomtype = ClassroomTP.objects.get(id = roomid)
            return render(request, "AllokAcads/ambient_edit_roomtypes.html", {'roomtype': roomtype, 'ambient': ambient, 'roomid': roomid, 'user': user})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_roomtypes_validate(request, roomid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            name = request.POST.get('name')    
            roomtype = ClassroomTP.objects.get(id = roomid)
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
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            roomtype = ClassroomTP.objects.get(id = roomid)
            roomtype.delete()
            return redirect(f'/ambient/resources/roomtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_admtypes(request, admtypeid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            admtp = AdminTP.objects.get(id = admtypeid)
            return render(request, "AllokAcads/ambient_edit_admintypes.html", {'admtp': admtp, 'ambient': ambient, 'admtypeid': admtypeid, 'user': user})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_edit_admtypes_validate(request, admtypeid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            if request.POST.get('name'):
                name = request.POST.get('name')
            can_configure_ambient = True if request.POST.get('can_configure_ambient') == 'on' else False
            can_gerenciate_members = True if request.POST.get('can_gerenciate_members') == 'on' else False
            can_register_resources = True if request.POST.get('can_register_resources') == 'on' else False
            can_run_atribuition = True if request.POST.get('can_run_atribuition') == 'on' else False
            can_run_alocation = True if request.POST.get('can_run_alocation') == 'on' else False

            admtp = AdminTP.objects.get(id = admtypeid)
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
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_register_resources:  
            admtype = AdminTP.objects.get(id = admtypeid)
            admtype.delete()
            return redirect(f'/ambient/resources/admtypes/{ambient.ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_subjects_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            ambient_instance = Ambient.objects.get(ambientid = ambientid)
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
            ambient_instance.subjects.add(subject)
            return redirect(f'/ambient/resources/subjects/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_rooms(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            rooms = ambient[0].classrooms.all()
            return render(request, "AllokAcads/ambient_rooms.html", {'ambient' : ambient[0], 'user' : user, 'rooms' : rooms, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_rooms(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            roomtypes = ambient[0].classroom_types.all()
            return render(request, "AllokAcads/ambient_create_rooms.html", {'ambient' : ambient[0], 'user' : user, 'roomtypes' : roomtypes, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_rooms_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            ambient_instance = Ambient.objects.get(ambientid = ambientid)
            name = request.POST.get('name')
            roomtype = ClassroomTP.objects.filter(id = request.POST.get('roomtype'))
            capacity = request.POST.get('capacity')
            if not roomtype:
                roomtype = None
            else: roomtype = roomtype[0]
            room = Classroom(name=name, classroom_type=roomtype, classroom_capacity=capacity, num_uses=0)
            room.save()
            ambient_instance.classrooms.add(room)
            return redirect(f'/ambient/resources/rooms/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_roomtypes(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            roomtypes = ambient[0].classroom_types.all()
            return render(request, "AllokAcads/ambient_roomtypes.html", {'ambient' : ambient[0], 'user' : user, 'roomtypes' : roomtypes, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_roomtypes(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            return render(request, "AllokAcads/ambient_create_roomtypes.html", {'ambient' : ambient[0], 'user' : user, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_roomtypes_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient_instance = Ambient.objects.get(ambientid = ambientid)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        name = request.POST.get('name')    
        roomtype = ClassroomTP(name=name)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            if roomtype:
                roomtype.save()
                ambient_instance.classroom_types.add(roomtype)
            return redirect(f'/ambient/resources/roomtypes/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_classes(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        classes = ambient[0].classes.all()
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            username = user.name
            return render(request, "AllokAcads/ambient_classes.html", {'ambient': ambient[0], 'user': user, 'userid': userid, 'username': username, 'classes': classes})
        else:
                return redirect('home')
    else:
        return redirect('/')

def ambient_create_classes(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            schedules = ambient[0].available_schedules.all()
            classrooms = ambient[0].classrooms.all()
            professors = ambient[0].members.all().filter(is_professor = True)
            subjects = ambient[0].subjects.all()
            columns = ambient[0].periods_in_a_day
            username = user.name
            return render(request, "AllokAcads/ambient_create_classes.html", {'ambient': ambient[0], 'user': user, 'userid': userid, 'username': username, 'classrooms': classrooms, 'professors': professors, 'subjects': subjects, 'schedules': schedules, 'columns': columns})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_create_classes_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            ambient_instance = Ambient.objects.get(ambientid = ambientid)
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
            ambient_instance.classes.add(tclass)
            return redirect(f'/ambient/resources/classes/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_formations(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            formations = ambient[0].formations.all()
            return render(request, "AllokAcads/ambient_formations.html", {'ambient' : ambient[0], 'user' : user, 'formations' : formations, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')

def ambient_create_formations(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            return render(request, "AllokAcads/ambient_create_formations.html", {'ambient' : ambient[0], 'user' : user, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_create_formations_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            ambient_instance = Ambient.objects.get(ambientid = ambientid)

            name = request.POST.get('name')    
            formation = Formation(name=name)
            if formation:
                formation.save()
                ambient_instance.formations.add(formation)
            return redirect(f'/ambient/resources/formations/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_admtypes(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            admtypes = ambient[0].admin_types.all()
            return render(request, "AllokAcads/ambient_admtypes.html", {'ambient' : ambient[0], 'user' : user, 'admtypes' : admtypes, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_create_admtypes(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            return render(request, "AllokAcads/ambient_create_admtypes.html", {'ambient' : ambient[0], 'user' : user, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_create_admtypes_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.filter(ambientid = ambientid)
        member = ambient[0].members.filter(user = user)
        if ambient[0].members.filter(user = user) and member[0].admin_type.can_register_resources:  
            ambient_instance = Ambient.objects.get(ambientid = ambientid)
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
                ambient_instance.admin_types.add(admtp)

            return redirect(f'/ambient/resources/admtypes/{ambient[0].ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_profile_edit(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        if ambient[0].members.filter(user = user):
            member = ambient[0].members.all().filter(user = user)
            formations = ambient[0].formations.all()
            return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient[0], 'user': user, 'formations' : formations, 'userid': userid, 'member': member[0]})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def ambient_profile_edit_validate(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.filter(ambientid = ambientid)
        if ambient[0].members.filter(user = user):
            member = ambient[0].members.get(user = user)
            registration = request.POST.get('register')
            formations = request.POST.getlist('member_formations')
            time_in_campus = request.POST.get('time_in_campus')
            time_in_institution = request.POST.get('time_in_institution')
            career_level = request.POST.get('career_level')
            if registration:
                member.registration = registration
            if formations:
                for formation in formations:
                    formation = Formation.objects.get(id = formation)
                    didatic_experience_time = request.POST.get(f"didatic_experience_time_{formation.id}")
                    professional_experience_time = request.POST.get(f"professional_experience_time_{formation.id}")
                    member_formation = Member_Formation(formation=formation, didactic_experience_time = didatic_experience_time, professional_experience_time = professional_experience_time)
                    member_formation.save()
                    member.formations.add(member_formation)
            if time_in_campus:
                member.time_in_campus = time_in_campus
            if time_in_institution:
                member.time_in_institution = time_in_institution
            if career_level:
                member.career_level = career_level
            member.save()
            formations = ambient[0].formations.all()
            return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient[0], 'user': user, 'formations' : formations, 'userid': userid, 'member': member})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def profile(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        picture = user.picture
        return render(request, "AllokAcads/profile.html", {'userid' : userid, 'user' : user, 'picture' : picture})
    else:
        return redirect('/')
    
def profile_edit(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        return render(request, "AllokAcads/profile_edit.html", {'userid' : userid, 'user' : user})
    else:
        return redirect('/')
    
def profile_edit_validate(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        picture = request.FILES.get('picture')
        name = request.POST.get('name')
        description = request.POST.get('description')
        if picture:
            picture_path = user.picture.path
            user.picture = picture
            os.remove(picture_path)
        if name:
            user.name = name
        if description:
            user.description = description
        user.save()
        return redirect(f'/home/profile')
    else:
        return redirect('/')
    
def enter_ambient(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambientid = request.POST.get('ambient_identificator')
        ambient = Ambient.objects.filter(ambientid = ambientid)
        if ambient:
            if not(userid in ambient[0].enter_solicitations):
                if not(ambient[0].members.filter(user = user)):
                    ambient[0].enter_solicitations.append(userid)
                    ambient[0].save()
                    messages.success(request, "Solicitação enviada, aguarde aprovação.")
                else:
                    messages.error(request, "Você já é membro deste ambiente.")
            else:
                messages.error(request, "Uma solicitação já foi enviada para este ambiente.")
        else:
            messages.error(request, "Ambiente não encontrado.")
            redirect(f'/home/')
        return redirect(f'/home')
    else:
        return redirect('/')
    
def professor_true(request, memberid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:
            member = ambient.members.all().get(id=memberid)
            member.is_professor = True
            member.save()
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def professor_false(request, memberid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:
            member = ambient.members.all().get(id=memberid)
            member.is_professor = False
            member.save()
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def change_position(request, memberid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userid = user.userid
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:
            member = ambient.members.get(id=memberid)
            admtypes = ambient.admin_types.all()
            return render(request, "AllokAcads/change_position.html", {'ambient' : ambient, 'member' : member, 'user' : user, 'admtypes' : admtypes, 'userid': userid})
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def remove_member(request, memberid, ambientid):
    if request.user.is_authenticated:
        print(ambientid)
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:
            member = ambient.members.get(id=memberid)
            member.user.ambients.remove(ambient.id)
            ambient.members.remove(memberid)
            if not ambient.members.exists():
                ambient.delete()
                return redirect('home')
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    return redirect('home')
    
def change_position_validate(request, memberid, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        tmember = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and tmember[0].admin_type.can_gerenciate_members:
            member = ambient.members.get(id=memberid)
            admtype = AdminTP.objects.get(id=request.POST.get('admtype'))
            member.admin_type = admtype
            member.save()
            return redirect(f'/ambient/members/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def check_conflitant_schedules_classroom(classroom, activitie):
    activities_with_classroom = list(Activitie.objects.filter(tclassroom = classroom))
    activities_with_classroom.append(activitie)
    num_activities = len(activities_with_classroom)
    available_sch_qtd = 0
    no_available_sch = None
    no_available_sch_qtd = 0
    for tactivitie in activities_with_classroom:
        available_schedules = 0
        last_column = 0
        last_line = 0
        for schedule in tactivitie.tclass.prefered_schedules.all():
            if (schedule.line == last_line and schedule.column > last_column) or (schedule.line != last_line) or (last_column == 0):
                available = False
                for i in range(tactivitie.activities_qtd):
                    schedule_range = Schedule_Preference.objects.get(id = schedule.id)
                    if schedule_range and tactivitie.tclass.prefered_schedules.filter(id = schedule_range.id):
                        available = True
                        last_line = schedule.line
                        last_column = schedule.column+i
                    else:
                        available = False
                if available: available_schedules += 1
        if available_schedules >= num_activities or available_schedules == 0:
            available_sch_qtd += 1
        else:
            available_schedules = 0
            activities_with_classroom2 = activities_with_classroom.remove(tactivitie)
            if activities_with_classroom2:
                num_activities2 = len(activities_with_classroom2)
                for tactivitie in activities_with_classroom2:
                    last_column = 0
                    last_line = 0
                    for schedule in tactivitie.tclass.prefered_schedules.all():
                        if ((schedule.line == last_line and schedule.column > last_column) or (schedule.line != last_line) or (last_column == 0) and schedule not in list(tactivitie.tprofessor.prefered_schedules.all())):
                            available = False
                            for i in range(tactivitie.activities_qtd):
                                schedule_range = Schedule_Preference.objects.get(id = schedule.id)
                                if schedule_range and tactivitie.tclass.prefered_schedules.filter(id = schedule_range.id):
                                    available = True
                                    last_line = schedule.line
                                    last_column = schedule.column+i
                                else:
                                    available = False
                            if available: available_schedules += 1
                    if available_schedules >= num_activities2 or available_schedules == 0:
                        available_sch_qtd += 1
                    else:
                        no_available_sch = tactivitie
                        no_available_sch_qtd += 1
    if available_sch_qtd == num_activities:
        return True
    else:
        weight1 = 0
        if classroom:
            classrooms_rooms = activitie.tclass.ideal_classrooms.filter(classroom = classroom)
            subjects_rooms = activitie.tsubject.ideal_classrooms.filter(classroom = classroom)
            if classrooms_rooms:
                weight1 = classrooms_rooms[0].classroom_weight
                if subjects_rooms:
                    weight1 += subjects_rooms[0].classroom_weight
            else:
                if subjects_rooms:
                    weight1 = subjects_rooms[0].classroom_weight

        weight2 = 0
        if no_available_sch:
            classrooms_rooms = activitie.tclass.ideal_classrooms.filter(classroom = no_available_sch.tclassroom)
            subjects_rooms = activitie.tsubject.ideal_classrooms.filter(classroom = no_available_sch.tclassroom)
            if classrooms_rooms:
                weight2 = classrooms_rooms[0].classroom_weight
                if subjects_rooms:
                    weight2 += subjects_rooms[0].classroom_weight
            else:
                if subjects_rooms:
                    weight2 = subjects_rooms[0].classroom_weight

            if weight1 > weight2:
                return no_available_sch
    return False


def check_conflitant_schedules_professor(professor, activitie):
    activities_with_professor = list(Activitie.objects.filter(tprofessor = professor))
    activities_with_professor.append(activitie)
    num_activities = len(activities_with_professor)
    available_sch_qtd = 0
    no_available_sch = None
    no_available_sch_qtd = 0
    for tactivitie in activities_with_professor:
        available_schedules = 0
        last_column = 0
        last_line = 0
        for schedule in tactivitie.tclass.prefered_schedules.all():
            if (schedule.line == last_line and schedule.column > last_column) or (schedule.line != last_line) or (last_column == 0):
                available = False
                for i in range(tactivitie.activities_qtd):
                    schedule_range = Schedule_Preference.objects.get(id = schedule.id)
                    if schedule_range and tactivitie.tclass.prefered_schedules.filter(id = schedule_range.id):
                        available = True
                        last_line = schedule.line
                        last_column = schedule.column+i
                    else:
                        available = False
                if available: available_schedules += 1
        if available_schedules >= num_activities or available_schedules == 0:
            available_sch_qtd += 1
        else:
            available_schedules = 0
            activities_with_professor2 = activities_with_professor.remove(tactivitie)
            if activities_with_professor2:
                for tactivitie in activities_with_professor2:
                    num_activities2 = len(activities_with_professor2)
                    last_column = 0
                    last_line = 0
                    for schedule in tactivitie.tclass.prefered_schedules.all():
                        if ((schedule.line == last_line and schedule.column > last_column) or (schedule.line != last_line) or (last_column == 0) and schedule not in list(tactivitie.tprofessor.prefered_schedules.all())):
                            available = False
                            for i in range(tactivitie.activities_qtd):
                                schedule_range = Schedule_Preference.objects.get(id = schedule.id)
                                if schedule_range and tactivitie.tclass.prefered_schedules.filter(id = schedule_range.id):
                                    available = True
                                    last_line = schedule.line
                                    last_column = schedule.column+i
                                else:
                                    available = False
                            if available: available_schedules += 1
                    if available_schedules >= num_activities2 or available_schedules == 0:
                        available_sch_qtd += 1
                    else:
                        no_available_sch = tactivitie
                        no_available_sch_qtd += 1
    if available_sch_qtd == num_activities:
        return True
    else:
        relevant_formations = activitie.tsubject.relevant_formations.all().order_by("-formation_weight")
        if no_available_sch and no_available_sch_qtd < 2:
            formations_1 = professor.formations.all()
            formations_2 = no_available_sch.tprofessor.formations.all()
            degree_1_count = 0
            degree_2_count = 0
            professional_experience_1_count = 0
            professional_experience_2_count = 0
            didatic_experience_1_count = 0
            didatic_experience_2_count = 0
            formation_1_count = 0
            formation_2_count = 0
            if activitie.tclass.favorite_professors.all().filter(professor = professor):
                tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
            if activitie.tsubject.favorite_professors.all().filter(professor = professor):
                tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
            if no_available_sch.tclass.favorite_professors.all().filter(professor = no_available_sch.tprofessor):
                tclassrooms_professor2 = no_available_sch.tclass.favorite_professors.all().get(professor = no_available_sch.tprofessor).professor_weight
            if no_available_sch.tsubject.favorite_professors.all().filter(professor = no_available_sch.tprofessor):
                tsubjects_professor2 = no_available_sch.tsubject.favorite_professors.all().get(professor = no_available_sch.tprofessor).professor_weight
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
            relevant_formations = no_available_sch.tsubject.relevant_formations.all().order_by("-formation_weight")
            for formation in relevant_formations:
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
                        formation_1_count *= formation.formation_weight
            if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2 or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100))):
                return no_available_sch
            elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2 or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100))):
                if degree_1_count > degree_2_count:
                    return no_available_sch
                elif degree_1_count == degree_2_count:
                    if professional_experience_1_count > professional_experience_2_count:
                        return no_available_sch
                    elif professional_experience_1_count == professional_experience_2_count:
                        if didatic_experience_1_count > didatic_experience_2_count:
                            return no_available_sch
                        elif didatic_experience_1_count == didatic_experience_2_count:
                            if professor.time_in_campus > no_available_sch.tprofessor.time_in_campus:
                                return no_available_sch
                            elif professor.time_in_campus == no_available_sch.tprofessor.time_in_campus:
                                if professor.time_in_institution > no_available_sch.tprofessor.time_in_institution:
                                    return no_available_sch
                                elif professor.time_in_institution == no_available_sch.tprofessor.time_in_institution:
                                    if datetime.date.today() - professor.user.birthdate > datetime.date.today() - no_available_sch.tprofessor.user.birthdate:
                                        return no_available_sch
                                    elif datetime.date.today() - professor.user.birthdate == datetime.date.today() - no_available_sch.tprofessor.user.birthdate:
                                        if formation_1_count >= formation_2_count:
                                            return no_available_sch
        return False 


def run_atribuition(request, ambientid):   
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_run_atribuition:
            ambient.activities.all().delete()
            ambient.activities.clear()
            ambient.save()
            classes = ambient.classes.all()
            rooms = ambient.classrooms.all()
            for room in rooms:
                room.num_uses = 0
                room.save()
            rooms = ambient.classrooms.all()
            professors = ambient.members.all().filter(is_professor = True)
            for professor in professors:
                professor.num_uses = 0
                professor.save()
            for aclass in classes:
                necessary_subjects = aclass.necessary_subjects.all()
                for subject in necessary_subjects:
                    activitie = Activitie(tclass = aclass, tsubject = subject.subject, activities_qtd = subject.periods)
                    activitie.save()
                    ambient.activities.add(activitie)
                    ambient.save()
            activities = ambient.activities.all()
            for activitie in activities:
                classrooms_rooms = activitie.tclass.ideal_classrooms.all().order_by("-classroom_weight")
                subjects_rooms = activitie.tsubject.ideal_classrooms.all().order_by("-classroom_weight")
                highest_weight = 0
                chosen_room = None
                for room in classrooms_rooms:
                    conflitant_classroom = check_conflitant_schedules_classroom(room.classroom, activitie)
                    if subjects_rooms.filter(classroom__name = room.classroom.name).exists():
                        subject_room = subjects_rooms.get(classroom__name = room.classroom.name)
                        weight = room.classroom_weight + subject_room.classroom_weight
                    else:
                        weight = room.classroom_weight
                    if weight > highest_weight and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                        highest_weight = weight
                        chosen_room = room.classroom  
                for room in subjects_rooms:
                    conflitant_classroom = check_conflitant_schedules_classroom(room.classroom, activitie)
                    weight = room.classroom_weight
                    if weight >= highest_weight and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                        highest_weight = weight
                        chosen_room = room.classroom
                if(highest_weight > 0 and chosen_room != None):
                    activitie.tclassroom = chosen_room
                    activitie.classroom_weight = highest_weight
                    activitie.save()
                    chosen_room.num_uses += activitie.activities_qtd
                    chosen_room.save()
                    if isinstance(conflitant_classroom, Activitie):
                        conflitant_classroom1 = conflitant_classroom.tclassroom
                        conflitant_classroom.tprofessor = None
                        conflitant_classroom1 -= conflitant_classroom.activities_qtd
                        conflitant_classroom.save()
                        conflitant_classroom1.save()
            for i in range(10):
                average_occupation = 0
                for room in rooms:
                    average_occupation += room.num_uses   
                average_occupation = average_occupation/len(rooms)   
                activities = ambient.activities.all()
                for activitie in activities:
                    rooms = ambient.classrooms.all()
                    if activitie.tclassroom.num_uses > average_occupation:
                        classrooms_rooms = activitie.tclass.ideal_classrooms.all().order_by("-classroom_weight")
                        subjects_rooms = activitie.tsubject.ideal_classrooms.all().order_by("-classroom_weight")
                        second_classrooms_rooms = classrooms_rooms.exclude(classroom=activitie.tclassroom)
                        second_subjects_rooms = subjects_rooms.exclude(classroom=activitie.tclassroom)
                        highest_weight = 0
                        chosen_room = None
                        for room in second_classrooms_rooms:
                            conflitant_classroom = check_conflitant_schedules_classroom(room.classroom, activitie)
                            if second_subjects_rooms.filter(classroom__name = room.classroom.name).exists():
                                subject_room = second_subjects_rooms.get(classroom__name = room.classroom.name)
                                weight = room.classroom_weight + subject_room.classroom_weight
                            else:
                                weight = room.classroom_weight
                            if weight > highest_weight and activitie.tclassroom.num_uses - room.classroom.num_uses >= 2 and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                                highest_weight = weight
                                chosen_room = room.classroom
                        for room in second_subjects_rooms:
                            conflitant_classroom = check_conflitant_schedules_classroom(room.classroom, activitie)
                            weight = room.classroom_weight
                            if weight >= highest_weight and activitie.tclassroom.num_uses - room.classroom.num_uses >= 2 and room.classroom.classroom_capacity >= activitie.tclass.number_of_students and conflitant_classroom:
                                highest_weight = weight
                                chosen_room = room.classroom
                        if(highest_weight > 0 and chosen_room != None):
                            classroom_save = activitie.tclassroom
                            classroom_save.num_uses -= activitie.activities_qtd
                            activitie.tclassroom = chosen_room
                            activitie.classroom_weight = highest_weight
                            chosen_room.num_uses += activitie.activities_qtd
                            chosen_room.save()
                            classroom_save.save()
                            activitie.save()
                            if isinstance(conflitant_classroom, Activitie):
                                conflitant_classroom1 = conflitant_classroom.tclassroom
                                conflitant_classroom.tprofessor = None
                                conflitant_classroom1 -= conflitant_classroom.activities_qtd
                                conflitant_classroom.save()
                                conflitant_classroom1.save()
                        elif activitie.classroom_weight < 100:
                            chosen_room = None
                            similar_rooms = Classroom.objects.filter(classroom_type = activitie.tclassroom.classroom_type)
                            for room in similar_rooms:
                                if activitie.tclassroom.num_uses - room.num_uses >= 2 and room.classroom_capacity >= activitie.tclass.number_of_students:
                                    chosen_room = room
                            if chosen_room:
                                classroom_save = activitie.tclassroom
                                classroom_save.num_uses -= activitie.activities_qtd
                                activitie.tclassroom = chosen_room
                                activitie.classroom_weight = highest_weight
                                chosen_room.num_uses += activitie.activities_qtd
                                chosen_room.save()
                                classroom_save.save()
                                activitie.save()
                                if isinstance(conflitant_classroom, Activitie):
                                    conflitant_classroom1 = conflitant_classroom.tclassroom
                                    conflitant_classroom.tprofessor = None
                                    conflitant_classroom1 -= conflitant_classroom.activities_qtd
                                    conflitant_classroom.save()
                                    conflitant_classroom1.save()

            #inicio da atribuição de professores
            activities = ambient.activities.all()
            for activitie in activities:
                relevant_formations = activitie.tsubject.relevant_formations.all().order_by("-formation_weight")
                if activitie.tclass.favorite_professors or activitie.tsubject.favorite_professors:
                    classrooms_professors = activitie.tclass.favorite_professors.all().order_by("-professor_weight")
                    subjects_professors = activitie.tsubject.favorite_professors.all().order_by("-professor_weight")
                highest_weight = 0
                chosen_professor = None
                fixed = 0
                swap = 0
                swapAct = None
                subject_professor = 1
                for professor in classrooms_professors:
                    if subjects_professors.filter(professor = professor.professor).exists():
                        subject_professor = subjects_professors.get(professor = professor.professor)
                        weight = professor.professor_weight + subject_professor.professor_weight
                    else:
                        weight = professor.professor_weight
                    if professor.professor.num_uses >= ambient.max_actv_in_cicle:
                        current_activities = Activitie.objects.filter(tprofessor = professor.professor).order_by("professor_weight")
                        smallest_weight = current_activities[0]
                        if smallest_weight.professor_weight < weight:
                            fixed = 1
                        elif smallest_weight.professor_weight == weight:
                            preference1 = professor.professor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0
                            preference2 = smallest_weight.tprofessor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0
                            if preference1 > preference2:
                                fixed = 1
                    if fixed == 0 and ((professor.professor.num_uses + activitie.tclass.necessary_subjects.get(subject = activitie.tsubject).periods <= ambient.max_actv_in_cicle) or (professor.professor_weight == 100 or subject_professor == 100)):
                        if (weight > highest_weight):
                            if subjects_professors.filter(professor = professor.professor):
                                subject_professor = subjects_professors.get(professor = professor.professor).professor_weight
                            if(professor.professor_weight != 0 and subject_professor != 0):
                                highest_weight = weight
                                chosen_professor = professor.professor
                                swap = 0
                                swapAct = None
                        elif (weight == highest_weight):
                            formations_1 = professor.professor.formations.all()
                            formations_2 = chosen_professor.formations.all()
                            degree_1_count = 0
                            degree_2_count = 0
                            professional_experience_1_count = 0
                            professional_experience_2_count = 0
                            didatic_experience_1_count = 0
                            didatic_experience_2_count = 0
                            formation_1_count = 0
                            formation_2_count = 0
                            if activitie.tclass.favorite_professors.all().filter(professor = professor.professor):
                                tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = professor.professor):
                                tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            for formation in relevant_formations:
                                for a_formation in formations_1:
                                    if a_formation.formation == formation:
                                        professional_experience_1_count = formation.professional_experience_time
                                        didatic_experience_1_count = formation.didatic_experience_time
                                        if a_formation.formation_degree == 'Graduado':
                                            degree_2_count += 25
                                        elif a_formation.formation_degree == 'Mestre':
                                            degree_2_count += 50
                                        elif a_formation.formation_degree == 'Doutor':
                                            degree_2_count += 100
                                        formation_1_count *= formation.formation_weight
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
                                        formation_1_count *= formation.formation_weight
                            if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2 or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100))):
                                highest_weight = weight
                                if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                    subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                if(professor.professor_weight != 0 and subject_professor != 0):
                                    chosen_professor = professor.professor
                                    swap = 0
                                    swapAct = None
                            elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2 or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100))):
                                if degree_1_count > degree_2_count:
                                    highest_weight = weight
                                    if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                        subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                    if(professor.professor_weight != 0 and subject_professor != 0):
                                        chosen_professor = professor.professor
                                        swap = 0
                                        swapAct = None
                                elif degree_1_count == degree_2_count:
                                    if professional_experience_1_count > professional_experience_2_count:
                                        highest_weight = weight
                                        if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                            subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                        if(professor.professor_weight != 0 and subject_professor != 0):
                                            chosen_professor = professor.professor
                                            swap = 0
                                            swapAct = None
                                    elif professional_experience_1_count == professional_experience_2_count:
                                        if didatic_experience_1_count > didatic_experience_2_count:
                                            highest_weight = weight
                                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                            if(professor.professor_weight != 0 and subject_professor != 0):
                                                chosen_professor = professor.professor
                                                swap = 0
                                                swapAct = None
                                        elif didatic_experience_1_count == didatic_experience_2_count:
                                            if professor.professor.time_in_campus > chosen_professor.time_in_campus:
                                                highest_weight = weight
                                                if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                    subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                if(professor.professor_weight != 0 and subject_professor != 0):
                                                    chosen_professor = professor.professor
                                                    swap = 0
                                                    swapAct = None
                                            elif professor.professor.time_in_campus == chosen_professor.time_in_campus:
                                                if professor.professor.time_in_institution > chosen_professor.time_in_institution:
                                                    highest_weight = weight
                                                    if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                        subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                    if(professor.professor_weight != 0 and subject_professor != 0):
                                                        chosen_professor = professor.professor
                                                        swap = 0
                                                        swapAct = None
                                                elif professor.professor.time_in_institution == chosen_professor.time_in_institution:
                                                    if datetime.date.today() - professor.professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                        highest_weight = weight
                                                        if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                            subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                        if(professor.professor_weight != 0 and subject_professor != 0):
                                                            chosen_professor = professor.professor
                                                            swap = 0
                                                            swapAct = None
                                                    elif datetime.date.today() - professor.professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
                                                        if formation_1_count >= formation_2_count:
                                                            highest_weight = weight
                                                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                            if(professor.professor_weight != 0 and subject_professor != 0):
                                                                chosen_professor = professor.professor
                                                                swap = 0
                                                                swapAct = None
                    elif fixed == 1:
                        if (weight > highest_weight or (professor.professor_weight == 100 or subject_professor == 100)):
                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid)
                            if(professor.professor_weight != 0 and subject_professor != 0):
                                highest_weight = weight
                                chosen_professor = professor.professor
                                swap = 1
                                swapAct = smallest_weight
                        elif (weight == highest_weight and weight > 0) or (professor.professor_weight == 100 or subject_professor == 100):
                            formations_1 = professor.professor.formations.all()
                            formations_2 = chosen_professor.formations.all()
                            degree_1_count = 0
                            degree_2_count = 0
                            professional_experience_1_count = 0
                            professional_experience_2_count = 0
                            didatic_experience_1_count = 0
                            didatic_experience_2_count = 0
                            formation_1_count = 0
                            formation_2_count = 0
                            if activitie.tclass.favorite_professors.all().filter(professor = professor.professor):
                                tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = professor.professor):
                                tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            for formation in relevant_formations:
                                for a_formation in formations_1:
                                    if a_formation.formation == formation:
                                        professional_experience_1_count = formation.professional_experience_time
                                        didatic_experience_1_count = formation.didatic_experience_time
                                        if a_formation.formation_degree == 'Graduado':
                                            degree_2_count += 25
                                        elif a_formation.formation_degree == 'Mestre':
                                            degree_2_count += 50
                                        elif a_formation.formation_degree == 'Doutor':
                                            degree_2_count += 100
                                        formation_1_count *= formation.formation_weight
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
                                        formation_1_count *= formation.formation_weight
                            if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                highest_weight = weight
                                if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                    subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                if(professor.professor_weight != 0 and subject_professor != 0):
                                    chosen_professor = professor.professor
                                    swap = 1
                                    swapAct = smallest_weight
                            elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if degree_1_count > degree_2_count:
                                    if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                        subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                    if(professor.professor_weight != 0 and subject_professor != 0):
                                        highest_weight = weight
                                        chosen_professor = professor.professor
                                        swap = 1
                                        swapAct = smallest_weight
                                elif degree_1_count == degree_2_count:
                                    if professional_experience_1_count > professional_experience_2_count:
                                        if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                            subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                        if(professor.professor_weight != 0 and subject_professor != 0):
                                            highest_weight = weight
                                            chosen_professor = professor.professor
                                            swap = 1
                                            swapAct = smallest_weight
                                    elif professional_experience_1_count == professional_experience_2_count:
                                        if didatic_experience_1_count > didatic_experience_2_count:
                                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                            if(professor.professor_weight != 0 and subject_professor != 0):
                                                highest_weight = weight
                                                chosen_professor = professor.professor
                                                swap = 1
                                                swapAct = smallest_weight
                                        elif didatic_experience_1_count == didatic_experience_2_count:
                                            if professor.professor.time_in_campus > chosen_professor.time_in_campus:
                                                if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                    subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                if(professor.professor_weight != 0 and subject_professor != 0):
                                                    highest_weight = weight
                                                    chosen_professor = professor.professor
                                                    swap = 1
                                                    swapAct = smallest_weight
                                            elif professor.professor.time_in_campus == chosen_professor.time_in_campus:
                                                if professor.professor.time_in_institution > chosen_professor.time_in_institution:
                                                    if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                        subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                    if(professor.professor_weight != 0 and subject_professor != 0):
                                                        highest_weight = weight
                                                        chosen_professor = professor.professor
                                                        swap = 1
                                                        swapAct = smallest_weight
                                                elif professor.professor.time_in_institution == chosen_professor.time_in_institution:
                                                    if datetime.date.today() - professor.professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                        if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                            subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                        if(professor.professor_weight != 0 and subject_professor != 0):
                                                            highest_weight = weight
                                                            chosen_professor = professor.professor
                                                            swap = 1
                                                            swapAct = smallest_weight
                                                    elif datetime.date.today() - professor.professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
                                                        if formation_1_count >= formation_2_count:
                                                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                            if(professor.professor_weight != 0 and subject_professor != 0):
                                                                highest_weight = weight
                                                                chosen_professor = professor.professor
                                                                swap = 1
                                                                swapAct = smallest_weight
                        fixed = 0
                for professor in subjects_professors:
                    weight = professor.professor_weight
                    if professor.professor.num_uses >= ambient.max_actv_in_cicle:
                        current_activities = Activitie.objects.filter(tprofessor = professor.professor).order_by("-professor_weight")
                        smallest_weight = current_activities[0]
                        if smallest_weight.professor_weight < weight:
                            fixed = 1
                        elif smallest_weight.professor_weight == weight:
                            preference1 = (professor.professor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0)
                            preference2 = (smallest_weight.tprofessor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0)
                            if preference1 > preference2:
                                fixed = 1
                    if fixed == 0 and (professor.professor.num_uses + activitie.tclass.necessary_subjects.get(subject = activitie.tsubject).periods <= ambient.max_actv_in_cicle) or (professor.professor_weight == 100):
                        if (weight > highest_weight):
                            if(professor.professor_weight != 0):
                                highest_weight = weight
                                chosen_professor = professor.professor
                                swap = 0
                                swapAct = None
                        elif (weight == highest_weight):
                            formations_1 = professor.professor.formations.all()
                            formations_2 = chosen_professor.formations.all()
                            degree_1_count = 0
                            degree_2_count = 0
                            professional_experience_1_count = 0
                            professional_experience_2_count = 0
                            didatic_experience_1_count = 0
                            didatic_experience_2_count = 0
                            formation_1_count = 0
                            formation_2_count = 0
                            tclassrooms_professor1 = 0
                            tsubjects_professor1 = 0
                            tclassrooms_professor2 = 0
                            tsubjects_professor2 = 0
                            if activitie.tclass.favorite_professors.all().filter(professor = professor.professor):
                                tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = professor.professor):
                                tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            for formation in relevant_formations:
                                for a_formation in formations_1:
                                    if a_formation.formation == formation:
                                        professional_experience_1_count = formation.professional_experience_time
                                        didatic_experience_1_count = formation.didatic_experience_time
                                        if a_formation.formation_degree == 'Graduado':
                                            degree_2_count += 25
                                        elif a_formation.formation_degree == 'Mestre':
                                            degree_2_count += 50
                                        elif a_formation.formation_degree == 'Doutor':
                                            degree_2_count += 100
                                        formation_1_count *= formation.formation_weight
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
                                        formation_1_count *= formation.formation_weight
                            if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if(professor.professor_weight != 0):
                                    highest_weight = weight
                                    chosen_professor = professor.professor
                                    swap = 0
                                    swapAct = None
                            elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if degree_1_count > degree_2_count:
                                    if(professor.professor_weight != 0):
                                        highest_weight = weight
                                        chosen_professor = professor.professor
                                        swap = 0
                                        swapAct = None
                                elif degree_1_count == degree_2_count:
                                    if professional_experience_1_count > professional_experience_2_count:
                                        if(professor.professor_weight != 0):
                                            highest_weight = weight
                                            chosen_professor = professor.professor
                                            swap = 0
                                            swapAct = None
                                    elif professional_experience_1_count == professional_experience_2_count:
                                        if didatic_experience_1_count > didatic_experience_2_count:
                                            if(professor.professor_weight != 0):
                                                highest_weight = weight
                                                chosen_professor = professor.professor
                                                swap = 0
                                                swapAct = None
                                        elif didatic_experience_1_count == didatic_experience_2_count:
                                            if professor.professor.time_in_campus > chosen_professor.time_in_campus:
                                                if(professor.professor_weight != 0):
                                                    highest_weight = weight
                                                    chosen_professor = professor.professor
                                                    swap = 0
                                                    swapAct = None
                                            elif professor.professor.time_in_campus == chosen_professor.time_in_campus:
                                                if professor.professor.time_in_institution > chosen_professor.time_in_institution:
                                                    if(professor.professor_weight != 0):
                                                        highest_weight = weight
                                                        chosen_professor = professor.professor
                                                        swap = 0
                                                        swapAct = None
                                                elif professor.professor.time_in_institution == chosen_professor.time_in_institution:
                                                    if datetime.date.today() - professor.professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                        if(professor.professor_weight != 0):
                                                            highest_weight = weight
                                                            chosen_professor = professor.professor
                                                            swap = 0
                                                            swapAct = None
                                                    elif datetime.date.today() - professor.professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
                                                        if formation_1_count >= formation_2_count:
                                                            if(professor.professor_weight != 0):
                                                                highest_weight = weight
                                                                chosen_professor = professor.professor
                                                                swap = 0
                                                                swapAct = None
                    elif fixed == 1:
                        if (weight == highest_weight and weight > 0) or (professor.professor_weight == 100):
                            if(professor.professor_weight != 0):
                                highest_weight = weight
                                chosen_professor = professor.professor
                                swap = 1
                        elif (weight == highest_weight and weight > 0) or (professor.professor_weight == 100):
                            formations_1 = professor.professor.professor.formations.all()
                            formations_2 = chosen_professor.formations.all()
                            degree_1_count = 0
                            degree_2_count = 0
                            professional_experience_1_count = 0
                            professional_experience_2_count = 0
                            didatic_experience_1_count = 0
                            didatic_experience_2_count = 0
                            formation_1_count = 0
                            formation_2_count = 0
                            tclassrooms_professor1 = 0
                            tsubjects_professor1 = 0
                            tclassrooms_professor2 = 0
                            tsubjects_professor2 = 0
                            if activitie.tclass.favorite_professors.all().filter(professor = professor.professor):
                                tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = professor.professor):
                                tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor.professor).professor_weight
                            if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            for formation in relevant_formations:
                                for a_formation in formations_1:
                                    if a_formation.formation == formation:
                                        professional_experience_1_count = formation.professional_experience_time
                                        didatic_experience_1_count = formation.didatic_experience_time
                                        if a_formation.formation_degree == 'Graduado':
                                            degree_2_count += 25
                                        elif a_formation.formation_degree == 'Mestre':
                                            degree_2_count += 50
                                        elif a_formation.formation_degree == 'Doutor':
                                            degree_2_count += 100
                                        formation_1_count *= formation.formation_weight
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
                                        formation_1_count *= formation.formation_weight
                            if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if(professor.professor_weight != 0):
                                    highest_weight = weight
                                    chosen_professor = professor.professor
                                    swap = 1
                                    swapAct = smallest_weight
                            elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if degree_1_count > degree_2_count:
                                    if(professor.professor_weight != 0):
                                        highest_weight = weight
                                        chosen_professor = professor.professor
                                        swap = 1
                                        swapAct = smallest_weight
                                elif degree_1_count == degree_2_count:
                                    if professional_experience_1_count > professional_experience_2_count:
                                        if(professor.professor_weight != 0):
                                            highest_weight = weight
                                            chosen_professor = professor.professor
                                            swap = 1
                                            swapAct = smallest_weight
                                    elif professional_experience_1_count == professional_experience_2_count:
                                        if didatic_experience_1_count > didatic_experience_2_count:
                                            if(professor.professor_weight != 0):
                                                highest_weight = weight
                                                chosen_professor = professor.professor
                                                swap = 1
                                                swapAct = smallest_weight
                                        elif didatic_experience_1_count == didatic_experience_2_count:
                                            if professor.professor.professor.time_in_campus > chosen_professor.time_in_campus:
                                                if(professor.professor_weight != 0):
                                                    highest_weight = weight
                                                    chosen_professor = professor.professor
                                                    swap = 1
                                                    swapAct = smallest_weight
                                            elif professor.professor.professor.time_in_campus == chosen_professor.time_in_campus:
                                                if professor.professor.professor.time_in_institution > chosen_professor.time_in_institution:
                                                    if(professor.professor_weight != 0):
                                                        highest_weight = weight
                                                        chosen_professor = professor.professor
                                                        swap = 1
                                                        swapAct = smallest_weight
                                                elif professor.professor.professor.time_in_institution == chosen_professor.time_in_institution:
                                                    if datetime.date.today() - professor.professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                        if(professor.professor_weight != 0):
                                                            highest_weight = weight
                                                            chosen_professor = professor.professor
                                                            swap = 1
                                                            swapAct = smallest_weight
                                                    elif datetime.date.today() - professor.professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
                                                        if formation_1_count >= formation_2_count:
                                                            if(professor.professor_weight != 0):
                                                                highest_weight = weight
                                                                chosen_professor = professor.professor
                                                                swap = 1
                                                                swapAct = smallest_weight
                        fixed = 0
                if(highest_weight > 0 and chosen_professor != None):
                    activitie.tprofessor = chosen_professor
                    activitie.professor_weight = highest_weight
                    activitie.save()
                    if (swap) and (activitie.tclass.favorite_professors.get(professor = swapAct.tprofessor).professor_weight != 100) and (activitie.tsubject.favorite_professors.get(professor = swapAct.tprofessor).professor_weight != 100):
                        swapAct.tprofessor = None
                        swapAct.professor_weight = 0
                        swapAct.save()
                    else:
                        chosen_professor.num_uses += activitie.tclass.necessary_subjects.get(subject = activitie.tsubject).periods
                        chosen_professor.save()
            
            
            #até aqui é quase garantido que todas as preferencias de materia e turma foram atendidas
            
            
            subjects = ambient.subjects.all()
            for subject in subjects:
                relevant_formations = subject.relevant_formations.all().order_by("-formation_weight")
                relevant_professors = ambient.members.all().filter(is_professor = True, prefered_subjects__subject = subject)
                highest_weight = 0
                chosen_professor = None
                subject_preference = 1
                selected = 1

                while(ambient.activities.all().filter(tsubject = subject, tprofessor = None) and relevant_professors and selected != 0):
                    for professor in relevant_professors:
                        professor_subject = professor.prefered_subjects.get(subject = subject)
                        if professor.num_uses < ambient.max_actv_in_cicle and professor_subject.subject_weight > highest_weight:
                            if(subject.favorite_professors.all().filter(professor = professor)):
                                subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                            if subject_preference != 0:
                                chosen_professor = professor
                                highest_weight = professor_subject.subject_weight
                        elif professor.num_uses < ambient.max_actv_in_cicle and professor_subject.subject_weight == highest_weight:
                            formations_1 = professor.formations.all()
                            formations_2 = chosen_professor.formations.all()
                            degree_1_count = 0
                            degree_2_count = 0
                            professional_experience_1_count = 0
                            professional_experience_2_count = 0
                            didatic_experience_1_count = 0
                            didatic_experience_2_count = 0
                            formation_1_count = 0
                            formation_2_count = 0
                            tclassrooms_professor1 = 0
                            tsubjects_professor1 = 0
                            tclassrooms_professor2 = 0
                            tsubjects_professor2 = 0
                            subject_1 = 0
                            subject_2 = 0
                            if subject.favorite_professors.all().filter(professor = professor):
                                subject_1 = subject.favorite_professors.all().get(professor = professor).professor_weight
                            if subject.favorite_professors.all().filter(professor = chosen_professor):
                                subject_2 = subject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                            for formation in relevant_formations:
                                for a_formation in formations_1:
                                    if a_formation.formation == formation:
                                        professional_experience_1_count = formation.professional_experience_time
                                        didatic_experience_1_count = formation.didatic_experience_time
                                        if a_formation.formation_degree == 'Graduado':
                                            degree_2_count += 25
                                        elif a_formation.formation_degree == 'Mestre':
                                            degree_2_count += 50
                                        elif a_formation.formation_degree == 'Doutor':
                                            degree_2_count += 100
                                        formation_1_count *= formation.formation_weight
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
                                        formation_1_count *= formation.formation_weight
                            if (subject_1 > subject_2) or ((subject_2 < 100) and (subject_1 == 100)):
                                if(subject.favorite_professors.all().filter(professor = professor)):
                                    subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                if subject_preference != 0:
                                    highest_weight = weight
                                    chosen_professor = professor
                            elif (subject_1 == subject_2) or ((subject_2 < 100) and (subject_1 == 100)):
                                if degree_1_count > degree_2_count:
                                    if(subject.favorite_professors.all().filter(professor = professor)):
                                        subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                    if subject_preference != 0:
                                        highest_weight = weight
                                        chosen_professor = professor
                                elif degree_1_count == degree_2_count:
                                    if professional_experience_1_count > professional_experience_2_count:
                                        if(subject.favorite_professors.all().filter(professor = professor)):
                                            subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                        if subject_preference != 0:
                                            highest_weight = weight
                                            chosen_professor = professor
                                    elif professional_experience_1_count == professional_experience_2_count:
                                        if didatic_experience_1_count > didatic_experience_2_count:
                                            if(subject.favorite_professors.all().filter(professor = professor)):
                                                subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                            if subject_preference != 0:
                                                highest_weight = weight
                                                chosen_professor = professor
                                        elif didatic_experience_1_count == didatic_experience_2_count:
                                            if professor.time_in_campus > chosen_professor.time_in_campus:
                                                if(subject.favorite_professors.all().filter(professor = professor)):
                                                    subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                                if subject_preference != 0:
                                                    highest_weight = weight
                                                    chosen_professor = professor
                                            elif professor.time_in_campus == chosen_professor.time_in_campus:
                                                if professor.time_in_institution > chosen_professor.time_in_institution:
                                                    if(subject.favorite_professors.all().filter(professor = professor)):
                                                        subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                                    if subject_preference != 0:
                                                        highest_weight = weight
                                                        chosen_professor = professor
                                                elif professor.time_in_institution == chosen_professor.time_in_institution:
                                                    if datetime.date.today() - professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                        if(subject.favorite_professors.all().filter(professor = professor)):
                                                            subject_preference = subject.favorite_professors.get(professor = professor).professor_weight
                                                        if subject_preference != 0:
                                                            highest_weight = weight
                                                            chosen_professor = professor

                    if chosen_professor:
                        num_uses = chosen_professor.num_uses
                        activities_with_subject = ambient.activities.all().filter(tsubject = subject)
                        activities_with_subject = sorted(activities_with_subject, key=lambda subject_activitie: sum(1 for schedule in subject_activitie.tclass.prefered_schedules.all() if chosen_professor.prefered_schedules.filter(id=schedule.id)), reverse=True)
                        for subject_activitie in activities_with_subject:
                            conflitant_schedules = check_conflitant_schedules_professor(chosen_professor, subject_activitie)
                            if (chosen_professor.num_uses + subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods <= ambient.max_actv_in_cicle) and (conflitant_schedules):
                                subject_preference = 1
                                class_preference = 1
                                if not(subject_activitie.tprofessor):
                                    if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                        subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                    if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                        class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                    if subject_preference != 0 and class_preference != 0:
                                        tactv = ambient.activities.get(id = subject_activitie.id)
                                        tactv.tprofessor = chosen_professor
                                        tactv.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                        tactv.save()
                                        chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                        chosen_professor.save()
                                        if isinstance(conflitant_schedules, Activitie):
                                            conflitant_professor = conflitant_schedules.tprofessor
                                            conflitant_schedules.tprofessor = None
                                            conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                            conflitant_schedules.save()
                                            conflitant_professor.save()
                                    
                                elif chosen_professor.num_uses + subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods <= ambient.max_actv_in_cicle:
                                    formations_1 = chosen_professor.formations.all()
                                    formations_2 = subject_activitie.tprofessor.formations.all()
                                    degree_1_count = 0
                                    degree_2_count = 0
                                    professional_experience_1_count = 0
                                    professional_experience_2_count = 0
                                    didatic_experience_1_count = 0
                                    didatic_experience_2_count = 0
                                    formation_1_count = 0
                                    formation_2_count = 0
                                    tclassrooms_professor1 = 0
                                    tsubjects_professor1 = 0
                                    tclassrooms_professor2 = 0
                                    tsubjects_professor2 = 0
                                    if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                        tclassrooms_professor1 = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                    if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                        tsubjects_professor1 = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                    if subject_activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                                        tclassrooms_professor2 = subject_activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                                    if subject_activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                                        tsubjects_professor2 = subject_activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
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
                                                formation_1_count *= formation.formation_weight
                                    if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                        if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                            subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                        if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                            class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                        if subject_preference != 0 and class_preference != 0:
                                            subject_activitie.tprofessor = chosen_professor
                                            subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                            subject_activitie.save()
                                            chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                            subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                            subject_activitie.tprofessor.num_uses.save()
                                            chosen_professor.save()
                                            if isinstance(conflitant_schedules, Activitie):
                                                conflitant_professor = conflitant_schedules.tprofessor
                                                conflitant_schedules.tprofessor = None
                                                conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                conflitant_schedules.save()
                                                conflitant_professor.save()
                                    elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                        if degree_1_count > degree_2_count:
                                            if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                            if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                            if subject_preference != 0 and class_preference != 0:
                                                subject_activitie.tprofessor = chosen_professor
                                                subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                subject_activitie.save()
                                                chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                subject_activitie.tprofessor.num_uses.save()
                                                chosen_professor.save()
                                                if isinstance(conflitant_schedules, Activitie):
                                                    conflitant_professor = conflitant_schedules.tprofessor
                                                    conflitant_schedules.tprofessor = None
                                                    conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                    conflitant_schedules.save()
                                                    conflitant_professor.save()
                                        elif degree_1_count == degree_2_count:
                                            if professional_experience_1_count > professional_experience_2_count:
                                                if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                    subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                                if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                    class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                                if subject_preference != 0 and class_preference != 0:
                                                    subject_activitie.tprofessor = chosen_professor
                                                    subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                    subject_activitie.save()
                                                    chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                    subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                    subject_activitie.tprofessor.num_uses.save()
                                                    chosen_professor.save()
                                                    if isinstance(conflitant_schedules, Activitie):
                                                        conflitant_professor = conflitant_schedules.tprofessor
                                                        conflitant_schedules.tprofessor = None
                                                        conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                        conflitant_schedules.save()
                                                        conflitant_professor.save()
                                            elif professional_experience_1_count == professional_experience_2_count:
                                                if didatic_experience_1_count > didatic_experience_2_count:
                                                    if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                        subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                                    if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                        class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                                    if subject_preference != 0 and class_preference != 0:
                                                        subject_activitie.tprofessor = chosen_professor
                                                        subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                        subject_activitie.save()
                                                        chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                        subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                        subject_activitie.tprofessor.num_uses.save()
                                                        chosen_professor.save()
                                                        if isinstance(conflitant_schedules, Activitie):
                                                            conflitant_professor = conflitant_schedules.tprofessor
                                                            conflitant_schedules.tprofessor = None
                                                            conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                            conflitant_schedules.save()
                                                            conflitant_professor.save()
                                                elif didatic_experience_1_count == didatic_experience_2_count:
                                                    if chosen_professor.time_in_campus > subject_activitie.tprofessor.time_in_campus:
                                                        if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                            subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                                        if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                            class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                                        if subject_preference != 0 and class_preference != 0:
                                                            subject_activitie.tprofessor = chosen_professor
                                                            subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                            subject_activitie.save()
                                                            chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                            subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                            subject_activitie.tprofessor.num_uses.save()
                                                            chosen_professor.save()
                                                            if isinstance(conflitant_schedules, Activitie):
                                                                conflitant_professor = conflitant_schedules.tprofessor
                                                                conflitant_schedules.tprofessor = None
                                                                conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                                conflitant_schedules.save()
                                                                conflitant_professor.save()
                                                    elif chosen_professor.time_in_campus == subject_activitie.tprofessor.time_in_campus:
                                                        if chosen_professor.time_in_institution > subject_activitie.tprofessor.time_in_institution:
                                                            if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                                subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                                            if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                                class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                                            if subject_preference != 0 and class_preference != 0:
                                                                subject_activitie.tprofessor = chosen_professor
                                                                subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                                subject_activitie.save()
                                                                chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                subject_activitie.tprofessor.num_uses.save()
                                                                chosen_professor.save()
                                                                if isinstance(conflitant_schedules, Activitie):
                                                                    conflitant_professor = conflitant_schedules.tprofessor
                                                                    conflitant_schedules.tprofessor = None
                                                                    conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                                    conflitant_schedules.save()
                                                                    conflitant_professor.save()
                                                        elif chosen_professor.time_in_institution == subject_activitie.tprofessor.time_in_institution:
                                                            if datetime.date.today() - chosen_professor.user.birthdate > datetime.date.today() - subject_activitie.tprofessor.user.birthdate:
                                                                if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                                    subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                                                if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                                    class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                                                if subject_preference != 0 and class_preference != 0:
                                                                    subject_activitie.tprofessor = chosen_professor
                                                                    subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                                    subject_activitie.save()
                                                                    chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                    subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                    subject_activitie.tprofessor.num_uses.save()
                                                                    chosen_professor.save()
                                                                    if isinstance(conflitant_schedules, Activitie):
                                                                        conflitant_professor = conflitant_schedules.tprofessor
                                                                        conflitant_schedules.tprofessor = None
                                                                        conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                                        conflitant_schedules.save()
                                                                        conflitant_professor.save()
                                                            elif datetime.date.today() - chosen_professor.user.birthdate == datetime.date.today() - subject_activitie.tprofessor.user.birthdate:
                                                                if formation_1_count > formation_2_count:
                                                                    if subject_activitie.tclass.favorite_professors.all().filter(professor = professor):
                                                                        subject_preference = subject_activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                                                                    if subject_activitie.tsubject.favorite_professors.all().filter(professor = professor):
                                                                        class_preference = subject_activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                                                                    if subject_preference != 0 and class_preference != 0:
                                                                        subject_activitie.tprofessor = chosen_professor
                                                                        subject_activitie.professor_weight = chosen_professor.prefered_subjects.all().get(subject = subject_activitie.tsubject).subject_weight
                                                                        subject_activitie.save()
                                                                        chosen_professor.num_uses += subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                        subject_activitie.tprofessor.num_uses -= subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods
                                                                        subject_activitie.tprofessor.num_uses.save()
                                                                        chosen_professor.save()
                                                                        if isinstance(conflitant_schedules, Activitie):
                                                                            conflitant_professor = conflitant_schedules.tprofessor
                                                                            conflitant_schedules.tprofessor = None
                                                                            conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                                                                            conflitant_schedules.save()
                                                                            conflitant_professor.save()
                            else: relevant_professors = relevant_professors.exclude(id=chosen_professor.id)
                        if num_uses == chosen_professor.num_uses:
                            selected = 0
                    else: selected = 0
                    
            #até aqui as aulas já devem estar distribuidas de acordo com a preferencia dos professores

            not_atribuited_activities = ambient.activities.all().filter(tprofessor = None)
            for not_atribuited_activitie in not_atribuited_activities:
                formations = not_atribuited_activitie.tsubject.relevant_formations.all().order_by("-formation_weight")
                chosen_professor = None
                highest_didatic_time = 0
                highest_professional_time = 0 
                highest_formation = 0 
                highest_weight = 0
                tclassrooms_professor1 = 0
                tsubjects_professor1 = 0
                tclassrooms_professor2 = 0
                tsubjects_professor2 = 0
                for a_formation in formations:
                    candidates = ambient.members.filter(is_professor = True, formations__formation = a_formation.formation)
                    for candidate in candidates:
                        conflitant_schedules = check_conflitant_schedules_professor(candidate, not_atribuited_activitie)
                        if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = candidate):
                            subject_preference = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = candidate).professor_weight
                        if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = candidate):
                            class_preference = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = candidate).professor_weight
                        if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = candidate):
                            tclassrooms_professor1 = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = candidate).professor_weight
                        if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = candidate):
                            tsubjects_professor1 = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = candidate).professor_weight
                        if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                            tclassrooms_professor2 = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                        if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                            tsubjects_professor2 = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                        if candidate.num_uses + not_atribuited_activitie.tclass.necessary_subjects.get(subject = not_atribuited_activitie.tsubject).periods <= ambient.max_actv_in_cicle:
                            if candidate.formation.formation_degree == 'Graduado':
                                degree = 25
                            elif candidate.formation.formation_degree == 'Mestre':
                                degree = 50
                            elif candidate.formation.formation.formation_degree == 'Doutor':
                                degree = 100
                            degree = a_formation.formation_weight * degree
                            if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                    highest_weight = weight
                                    chosen_professor = professor
                            elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                                if degree > highest_formation:
                                    if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                        highest_formation = degree
                                        chosen_professor = candidate
                                elif degree == highest_formation:
                                    if candidate.formation.professional_experience_time > highest_professional_time:
                                        if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                            highest_professional_time = candidate.formation.professional_experience_time
                                            chosen_professor = candidate
                                    elif candidate.formation.professional_experience_time == highest_professional_time:
                                        if candidate.formation.didatic_experience_time > highest_didatic_time:
                                            if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                                highest_didatic_time = candidate.formation.professional_didatic_time
                                                chosen_professor = candidate
                                        elif didatic_experience_1_count == didatic_experience_2_count:
                                            if candidate.time_in_campus > chosen_professor.tprofessor.time_in_campus:
                                                if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                                    highest_didatic_time = candidate.formation.professional_didatic_time
                                                    chosen_professor = candidate
                                            elif candidate.time_in_campus == chosen_professor.tprofessor.time_in_campus:
                                                if candidate.time_in_institution > chosen_professor.tprofessor.time_in_institution:
                                                    if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                                        highest_didatic_time = candidate.formation.professional_didatic_time
                                                        chosen_professor = candidate
                                                elif candidate.time_in_institution == chosen_professor.tprofessor.time_in_institution:
                                                    if datetime.date.today() - candidate.user.birthdate > datetime.date.today() - chosen_professor.tprofessor.user.birthdate:
                                                        if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                                            highest_didatic_time = candidate.formation.professional_didatic_time
                                                            chosen_professor = candidate
                                                    elif datetime.date.today() - candidate.user.birthdate == datetime.date.today() - chosen_professor.tprofessor.user.birthdate:
                                                        if formation_1_count > formation_2_count:
                                                            if subject_preference != 0 and class_preference != 0 and conflitant_schedules:
                                                                highest_didatic_time = candidate.formation.professional_didatic_time
                                                                chosen_professor = candidate
                                    
                if chosen_professor:
                    not_atribuited_activitie.tprofessor = chosen_professor
                    not_atribuited_activitie.professor_weight = highest_weight
                    not_atribuited_activitie.save()
                    chosen_professor.num_uses += activitie.tclass.necessary_subjects.get(subject = not_atribuited_activitie.tsubject).periods
                    chosen_professor.save()
                    if isinstance(conflitant_schedules, Activitie):
                        conflitant_professor = conflitant_schedules.tprofessor
                        conflitant_schedules.tprofessor = None
                        conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                        conflitant_schedules.save()
                        conflitant_professor.save()

            #garante que as atividades restantes sejam atribuídas a quem deve ser
                not_atribuited_activities = ambient.activities.all().filter(tprofessor = None)
                for not_atribuited_activitie in not_atribuited_activities:
                    candidates = ambient.members.all().filter(is_professor = True).order_by('num_uses')
                    highest_weight = 0
                    chosen_professor = None
                    for candidate in candidates:
                        conflitant_schedules = check_conflitant_schedules_professor(candidate, not_atribuited_activitie)
                        subject_preference = 1
                        class_preference = 1
                        if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = candidate):
                            subject_preference = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = candidate).professor_weight
                        if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = candidate):
                            class_preference = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = candidate).professor_weight
                        if candidate.num_uses + not_atribuited_activitie.tclass.necessary_subjects.get(subject = not_atribuited_activitie.tsubject).periods <= ambient.max_actv_in_cicle:
                            if subject_preference != 0 and class_preference != 0 and subject_preference + class_preference > highest_weight and conflitant_schedules:
                                highest_weight = subject_preference + class_preference
                                chosen_professor = candidate
                    if chosen_professor and highest_weight:
                        not_atribuited_activitie.tprofessor = chosen_professor
                        not_atribuited_activitie.professor_weight = 0
                        chosen_professor.num_uses += activitie.tclass.necessary_subjects.get(subject = activitie.tsubject).periods
                        not_atribuited_activitie.save()
                        chosen_professor.save()
                        if isinstance(conflitant_schedules, Activitie):
                            conflitant_professor = conflitant_schedules.tprofessor
                            conflitant_schedules.tprofessor = None
                            conflitant_professor.num_uses -= conflitant_schedules.activities_qtd
                            conflitant_schedules.save()
                            conflitant_professor.save()
                    
                #atribui randomicamente (deve gerar erro, e tbm gerar erro se houverem atividades em branco)


            return redirect(f'/ambient/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')

def run_alocation(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = ambient.members.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_run_alocation:
            timetable = Timetable(lines_number = ambient.periods_in_a_day, columns_number = ambient.days_in_a_cicle)
            timetable.save()
            ambient.published_timetable = timetable
            ambient.save()
            for schedule in ambient.available_schedules.all():
                alocation = Alocation(line = schedule.column, column = schedule.line)
                alocation.save()
                ambient.published_timetable.table.add(alocation)
                ambient.save()
            activities = ambient.activities.all()
            swap = True
            while(swap):
                swap = False
                for activitie in activities:
                    highest_weight = 0
                    chosen_sch = None
                    for schedule_c in activitie.tclass.prefered_schedules.all():
                        line = schedule_c.line
                        column = schedule_c.column
                        weight = 0
                        count_conflit = 0
                        conflit = None
                        p_weight = 0
                        for i in range(activitie.activities_qtd):
                            if activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i):

                                for alocation in ambient.published_timetable.table.all().filter(line = column+i, column = line):
                                    for actv in alocation.activitie.all():
                                        if((actv.tprofessor == activitie.tprofessor or actv.tclass == activitie.tclass or actv.tclassroom == activitie.tclassroom) and actv != conflit):
                                            count_conflit += 1
                                            conflit = actv
                                            if count_conflit > 1:
                                                break

                                if(conflit == None):
                                    ambient_sch = activitie.tclass.prefered_schedules.all().get(line=line, column=column+i)
                                    weight += 1
                                    if activitie.tprofessor.prefered_schedules.all().filter(id = ambient_sch.id):
                                        weight += 1

                                elif (count_conflit < 2):
                                    p_weight = 0
                                    p_ambient_sch = 0
                                    for j in range(activitie.activities_qtd):
                                        if activitie.tclass.prefered_schedules.all().filter(line=line, column=column+j):
                                            if not ambient.published_timetable.table.all().get(line = column+j, column = line).activitie:
                                                p_ambient_sch = activitie.tclass.prefered_schedules.all().get(line=line, column=column+j)
                                                p_weight += 1
                                                if activitie.tprofessor.prefered_schedules.all().filter(id = p_ambient_sch.id):
                                                    p_weight += 1

                                    t_weight = 0
                                    t_ambient_sch = 0
                                    t_activitie = conflit
                                    for j in range(t_activitie.activities_qtd):
                                        if t_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+j):
                                            t_ambient_sch = t_activitie.tclass.prefered_schedules.all().get(line=line, column=column+j)
                                            t_weight += 1
                                            if t_activitie.tprofessor.prefered_schedules.all().filter(id = t_ambient_sch.id):
                                                t_weight += 1
                                    
                                    if p_weight > t_weight:
                                        swap = True
                                        weight = p_weight
                                        chosen_sch = schedule_c
                                        change = True
                                    else:
                                        weight = 0
                                        break
                                else:
                                    weight = 0
                                    break
                            else:
                                weight = 0
                                break
                            

                        if weight > highest_weight:
                            chosen_sch = schedule_c
                            highest_weight = weight
                            if weight > p_weight:
                                change = False
                        
                    if highest_weight and chosen_sch:
                        for i in range(activitie.activities_qtd):
                            print(highest_weight, chosen_sch, chosen_sch.column+i, chosen_sch.line)
                            t_alocation = ambient.published_timetable.table.all().get(line = chosen_sch.column+i, column = chosen_sch.line)
                            print(t_alocation)
                            print(t_alocation.activitie.all())
                            t_alocation.activitie.add(activitie)
                            if change:
                                t_alocation.activitie.remove(t_activitie)
            
            not_alocated_activities = []
            for activitie in activities:
                if not ambient.published_timetable.table.all().filter(activitie = activitie):
                    not_alocated_activities.append(activitie)

            swap = True    
            while(swap):
                swap = False
                change = False
                for not_alocated_activitie in not_alocated_activities:
                    highest_weight = 0
                    chosen_sch = None
                    if not not_alocated_activitie.tclass.prefered_schedules and not_alocated_activitie.tprofessor.prefered_schedules:   
                        for schedule_c in not_alocated_activitie.tprofessor.prefered_schedules:
                            line = schedule_c.line
                            column = schedule_c.column
                            weight = 0        
                            count_conflit = 0
                            conflit = None
                            p_weight = 0
                            for i in range(not_alocated_activitie.activities_qtd):
                                if not_alocated_activitie.tprofessor.prefered_schedules.all().filter(line=line, column=column+i):
                                    
                                    for alocation in ambient.published_timetable.table.all().filter(line = column+i, column = line):
                                        for actv in alocation.activitie.all():
                                            if((actv.tprofessor == not_alocated_activitie.tprofessor or actv.tclass == not_alocated_activitie.tclass or actv.tclassroom == not_alocated_activitie.tclassroom) and actv != conflit):
                                                count_conflit += 1
                                                conflit = actv
                                                if count_conflit > 1:
                                                    break

                                    if (conflit == None):
                                        weight += 1
                                    elif(count_conflit < 2):
                                        p_weight = 0
                                        p_ambient_sch = 0
                                        for j in range(not_alocated_activitie.activities_qtd):
                                            if not_alocated_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+j):
                                                if not ambient.published_timetable.table.all().get(line = column+j, column = line).activitie:
                                                    p_ambient_sch = activitie.tclass.prefered_schedules.all().get(line=line, column=column+j)
                                                    p_weight += 1
                                                    if not_alocated_activitie.tprofessor.prefered_schedules.all().filter(id = p_ambient_sch.id):
                                                        p_weight += 1

                                        t_weight = 0
                                        t_ambient_sch = 0
                                        t_activitie = ambient.published_timetable.table.all().get(line = column+i, column = line).activitie
                                        for j in range(t_activitie.activities_qtd):
                                            if t_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+j):
                                                t_ambient_sch = t_activitie.tclass.prefered_schedules.all().get(line=line, column=column+j)
                                                t_weight += 1
                                                if t_activitie.tprofessor.prefered_schedules.all().filter(id = t_ambient_sch.id):
                                                    t_weight += 1

                                        if p_weight > t_weight:
                                            swap = True
                                            weight = p_weight
                                            chosen_sch = schedule_c
                                            change = True
                                        else:
                                            weight = 0
                                            break
                                    else:
                                        weight = 0
                                        break
                                else:
                                    weight = 0
                                    break
                                

                            if weight > highest_weight:
                                    chosen_sch = schedule_c
                                    highest_weight = weight
                                    t_alocation = ambient.published_timetable.table.all().get(line = chosen_sch.column+i, column = chosen_sch.line)
                                    if weight > p_weight:
                                        change = False
                    
                        if highest_weight and chosen_sch:
                            for i in range(not_alocated_activitie.activities_qtd):
                                t_alocation = ambient.published_timetable.table.all().get(line = chosen_sch.column+i, column = chosen_sch.line)
                                t_alocation.activitie.add(not_alocated_activitie)
                                if change:
                                    t_alocation.activitie.remove(t_activitie)
                        else:
                            ambient.published_timetable.not_alocated.add(activitie)
            return redirect(f'/ambient/{ambientid}')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def exit(request):
    if request.user.is_authenticated:
        logoutauth(request)
        return redirect('/')
    else:
        return redirect('/')
    
def ambient_delete(request, ambientid):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        ambient = Ambient.objects.get(ambientid = ambientid)
        member = Member.objects.filter(user = user)
        if ambient.members.filter(user = user) and member[0].admin_type.can_configure_ambient:  
            ambient.delete()
            return redirect('home')
        else:
            return redirect('home')
    else:
        return redirect('/')
    
def profile_delete(request):
    if request.user.is_authenticated:
        user = User.objects.get(userid = request.user.username)
        userauth = UserAuth.objects.get(id = user.id)
        user.delete()
        logoutauth(request)
        userauth.delete()
        return redirect('/')
    else:
        return redirect('/')
