from django.shortcuts import render, redirect
from django.conf import settings
import random, os, datetime, time
from .models import User, Ambient, Member, AdminTP, ClassroomTP, Formation, Subject, Formation_Preference, Classroom, Class, Professor_Preference, Classroom_Preference, Schedule_Preference, Class_Preference, Subject_Preference, Member_Formation, Activitie, Timetable, Alocation, Unregistered_Activitie
from shutil import copyfile
from django.db.models import Sum

# Create your views here.

def login(request):
    return render(request, "AllokAcads/login.html")

def login_validate(request):
    identificator = request.POST.get('id')
    password = request.POST.get('password')
   
    user = User.objects.filter(userid = identificator).filter(password = password)

    if(len(user) > 0):   
        return redirect(f'/AllokAcad/home/{identificator}')
    return redirect('/AllokAcad/login')

def register(request):
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
    name = request.POST.get('name')
    if not((len(name.strip()) > 0) and (len(name.strip()) <= 80)):
        return redirect('/AllokAcad/register')
    email = request.POST.get('email')
    if not((len(email.strip()) > 3) and (len(email.strip()) <= 320)):
        return redirect('/AllokAcad/register')
    password = request.POST.get('password')
    if not((len(password.strip()) > 5) and (len(password.strip()) <= 20)):
        return redirect('/AllokAcad/register')
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

    user = User(userid=identificator, picture=picture, name=name, email=email, password=password, birthdate=birthdate)
    user.save()

    return render(request, "AllokAcads/register.html")

def home(request, userid):
    user = User.objects.filter(userid = userid)
    ambients = user[0].ambients.all()
    username = user[0].name
    
    return render(request, "AllokAcads/home.html", {'username' : username, 'userid' : userid, 'ambients' : ambients})

def create_ambient(request, userid):
    return render(request, "AllokAcads/create_ambient.html", {'userid' : userid})

def generate_ambientid():
    identificator = ""
    for i in range(4):
        digit = chr(random.randint(65, 90))
        identificator += digit
    for i in range(5):
        digit = str(random.randint(0, 9))
        identificator += digit
    return identificator

def create_ambient_validate(request, userid):
    picture = request.FILES.get('picture')

    name = request.POST.get('name')
    if not((len(name.strip()) > 0) and (len(name.strip()) <= 80)):
        return redirect('/AllokAcad/register')
    description = request.POST.get('description')
    if not(len(name.strip()) <= 500):
        return redirect('/AllokAcad/register')

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
    
    user = User.objects.filter(userid = userid)

    creator = Member(user=user[0], admin_type=main_adm, is_professor=False)

    if not picture:
        directory = os.path.join(settings.BASE_DIR, f'media/ambients/{identificator}/ambient_picture')
        os.makedirs(directory, exist_ok=True)
        default_picture_path = os.path.join(settings.BASE_DIR, 'media', 'ambients/ambient.png')
        copyfile(default_picture_path, os.path.join(directory, 'ambient.png'))
        picture = f'ambients/{identificator}/ambient_picture/ambient.png'

    ambient = Ambient(ambientid=identificator, name=name, picture=picture, description=description)

    user[0].save()
    ambient.save()
    creator.save()

    user[0].ambients.add(ambient)
    ambient.admin_types.add(main_adm)
    ambient.members.add(creator)

    return redirect(f'/AllokAcad/home/{userid}')

def ambient(request, ambientid, userid):
  
    ambient = Ambient.objects.filter(ambientid=ambientid).first()
    user = User.objects.filter(userid=userid).first()
    
    if not ambient or not user:
        return redirect('home', userid=userid)
    
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
        'activities': activities
    })

def ambient_config(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid=ambientid)
    user = User.objects.filter(userid=userid)
    
    if ambient.exists() and user.exists():
        member = Member.objects.filter(ambient=ambient[0], user=user[0]).first()
        
        context = {
            'ambient': ambient[0],
            'user': user[0],
            'userid': userid, 
            'member': member
        }
        
        return render(request, "AllokAcads/ambient_config.html", context)
    else:
        return redirect('login')

def ambient_config_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
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
    if form_opening:
        ambient_instance.form_opening = form_opening
    if form_closing:
        ambient_instance.form_closing = form_closing
    if alt_solicitations_opening:
        ambient_instance.alt_solicitations_opening = alt_solicitations_opening
    if alt_solicitations_closing:
        ambient_instance.alt_solicitations_closing = alt_solicitations_closing
    if min_actv_in_a_day:
        ambient_instance.min_actv_in_day = min_actv_in_a_day
    if max_actv_in_a_day:
        ambient_instance.max_actv_in_day = min_actv_in_a_day
    if min_actv_in_a_cicle:
        ambient_instance.min_actv_in_cicle = min_actv_in_a_cicle
    if max_actv_in_a_cicle:
        ambient_instance.max_actv_in_cicle = max_actv_in_a_cicle

    ambient_instance.save()

    if (periods_in_a_day and days_in_a_cicle) or (periods_in_a_day and ambient_instance.days_in_a_cicle) or (ambient_instance.periods_in_a_day or days_in_a_cicle):
        ambient_instance.available_schedules.clear()
        for i in range(int(days_in_a_cicle)):
            for j in range(int(periods_in_a_day)):
                schedule = Schedule_Preference(line=i, column=j)
                schedule.save()
                ambient_instance.available_schedules.add(schedule)

    return redirect(f'/AllokAcad/ambient/config/{ambient[0].ambientid}/{user[0].userid}')

def ambient_profile(request, ambientid, userid):
    user = User.objects.filter(userid = userid)
    ambient = Ambient.objects.filter(ambientid = ambientid)
    
    if ambient.exists() and user.exists():
        ambient = ambient[0]
        user = user[0]
        username = user.name
        picture = user.picture
        
        context = {
            'ambient': ambient,
            'user': user,
            'userid': userid, 
            'username': username,  
            'picture': picture
        }
        
        return render(request, "AllokAcads/ambient_profile.html", context)
    else:
        return redirect('login')

def ambient_members(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    
    if ambient.exists() and user.exists():
        ambient = ambient[0]
        user = user[0]
        username = user.name
        members = ambient.members.all()
        context = {
            'ambient': ambient,
            'user': user,
            'userid': userid, 
            'username': username,  
            'members': members
        }
        
        return render(request, "AllokAcads/ambient_members.html", context)
    else:
        return redirect('login')

def ambient_form_validate(request, ambientid, userid):
    user = User.objects.filter(userid = userid)
    member = Member.objects.get(user = user[0])
    available_schedules = request.POST.getlist('available_schedules')
    prefered_classes = request.POST.getlist('prefered_classes')
    prefered_classrooms = request.POST.getlist('prefered_classrooms')
    prefered_subjects = request.POST.getlist('prefered_subjects')
    schedule_ids = request.POST.getlist("available_schedules")
    if schedule_ids:
        for schedule_id in schedule_ids:
            schedule = Schedule_Preference.objects.get(id = schedule_id)
            member.prefered_schedules.add(schedule)
    for available_schedule in available_schedules:
        schedule = Schedule_Preference.objects.get(id = available_schedule)
        member.prefered_schedules.add(schedule)
    for prefered_class in prefered_classes:
        tclass = Class.objects.get(id = prefered_class)
        class_weight = request.POST.get(f"class_weight_{prefered_class}")
        class_preference = Class_Preference(tclass=tclass, class_weight=class_weight)
        class_preference.save()
        member.prefered_classes.add(class_preference)
    for prefered_classroom in prefered_classrooms:
        classroom = Classroom.objects.get(id = prefered_classroom)
        classroom_weight = request.POST.get(f"classroom_weight_{prefered_classroom}")
        classroom_preference = Classroom_Preference(classroom=classroom, classroom_weight=classroom_weight)
        classroom_preference.save()
        member.prefered_classrooms.add(classroom_preference)
    for prefered_subject in prefered_subjects:
        subject = Subject.objects.get(id = prefered_subject)
        subject_weight = request.POST.get(f"subject_weight_{prefered_subject}")
        subject_preference = Subject_Preference(subject=subject, subject_weight=subject_weight)
        subject_preference.save()
        member.prefered_subjects.add(subject_preference)
    return redirect(f'/AllokAcad/ambient/{ambientid}/{userid}')

def ambient_solicitations(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    
    if ambient.exists() and user.exists():
        ambient = ambient[0]
        user = user[0]
        
        username = user.name
        
        solicitations = ambient.enter_solicitations
        names = []
        if solicitations:
            for solicitation in solicitations:
                name = User.objects.get(userid = solicitation).name
                names.append(name)
            solicitations_data = zip(names, solicitations)
        else:
            solicitations_data = []
            
        context = {
            'ambient': ambient,
            'user': user,
            'userid': userid,  
            'username': username, 
            'solicitations': solicitations_data
        }
        
        return render(request, "AllokAcads/ambient_solicitations.html", context)
    else:
        return redirect('login')

def accept_solicitation(request, memberid, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
    member = User.objects.get(userid = memberid)
    ambient.enter_solicitations.remove(memberid)
    new_member = Member(user=member, admin_type=None, is_professor=True)
    new_member.save()
    ambient.members.add(new_member)
    ambient.save()
    member.ambients.add(ambient)
    member.save()
    return redirect(f'/AllokAcad/ambient/solicitations/{ambientid}/{userid}')

def refuse_solicitation(request, memberid, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
    ambient.enter_solicitations.remove(memberid)
    ambient.save() 
    return redirect(f'/AllokAcad/ambient/solicitations/{ambientid}/{userid}')

def ambient_resources(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid=ambientid)
    user = User.objects.filter(userid=userid)
    
    if ambient.exists() and user.exists():
        ambient = ambient[0]
        user = user[0]
        
        username = user.name
        
        context = {
            'ambient': ambient,
            'user': user,
            'userid': userid, 
            'username': username
        }
        
        return render(request, "AllokAcads/ambient_resources.html", context)
    else:
        return redirect('login')

def ambient_subjects(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    subjects = ambient[0].subjects.all()
    return render(request, "AllokAcads/ambient_subjects.html", {'ambient' : ambient[0], 'user' : user[0], 'subjects' : subjects})

def ambient_create_subjects(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    classrooms = ambient[0].classrooms.all()
    professors = ambient[0].members.all().filter(is_professor = True)
    formations = ambient[0].formations.all()
    return render(request, "AllokAcads/ambient_create_subjects.html", {'ambient' : ambient[0], 'user' : user[0], 'classrooms' : classrooms, 'professors' : professors, 'formations' : formations})

def ambient_create_subjects_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
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
    return redirect(f'/AllokAcad/ambient/resources/subjects/{ambient[0].ambientid}/{user[0].userid}')

def ambient_rooms(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    rooms = ambient[0].classrooms.all()
    return render(request, "AllokAcads/ambient_rooms.html", {'ambient' : ambient[0], 'user' : user[0], 'rooms' : rooms})

def ambient_create_rooms(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    roomtypes = ambient[0].classroom_types.all()
    return render(request, "AllokAcads/ambient_create_rooms.html", {'ambient' : ambient[0], 'user' : user[0], 'roomtypes' : roomtypes})

def ambient_create_rooms_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    ambient_instance = Ambient.objects.get(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    name = request.POST.get('name')
    roomtype = ClassroomTP.objects.get(id = request.POST.get('roomtype'))
    capacity = request.POST.get('capacity')
    room = Classroom(name=name, classroom_type=roomtype, classroom_capacity=capacity, num_uses=0)
    room.save()
    ambient_instance.classrooms.add(room)
    return redirect(f'/AllokAcad/ambient/resources/rooms/{ambient[0].ambientid}/{user[0].userid}')

def ambient_roomtypes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    roomtypes = ambient[0].classroom_types.all()
    return render(request, "AllokAcads/ambient_roomtypes.html", {'ambient' : ambient[0], 'user' : user[0], 'roomtypes' : roomtypes})

def ambient_create_roomtypes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_create_roomtypes.html", {'ambient' : ambient[0], 'user' : user[0]})

def ambient_create_roomtypes_validate(request, ambientid, userid):
    ambient_instance = Ambient.objects.get(ambientid = ambientid)
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    name = request.POST.get('name')    
    roomtype = ClassroomTP(name=name)
    if roomtype:
        roomtype.save()
        ambient_instance.classroom_types.add(roomtype)
    return redirect(f'/AllokAcad/ambient/resources/roomtypes/{ambient[0].ambientid}/{user[0].userid}')

def ambient_classes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    classes = ambient[0].classes.all()
    return render(request, "AllokAcads/ambient_classes.html", {'ambient' : ambient[0], 'user' : user[0], 'classes' : classes})

def ambient_create_classes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    schedules = ambient[0].available_schedules.all()
    classrooms = ambient[0].classrooms.all()
    professors = ambient[0].members.all().filter(is_professor = True)
    subjects = ambient[0].subjects.all()
    columns = ambient[0].periods_in_a_day
    return render(request, "AllokAcads/ambient_create_classes.html", {'ambient' : ambient[0], 'user' : user[0], 'classrooms' : classrooms, 'professors' : professors, 'subjects' : subjects, 'schedules' : schedules, 'columns' : columns})

def ambient_create_classes_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
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
            if not periods:
                periods = 1
            subject = Subject.objects.get(id = subject_id)
            subject_preference = Subject_Preference(subject = subject, subject_weight = 100.0, periods = periods)
            subject_preference.save()
            tclass.necessary_subjects.add(subject_preference)
    ambient_instance.classes.add(tclass)
    return redirect(f'/AllokAcad/ambient/resources/classes/{ambient[0].ambientid}/{user[0].userid}')

def ambient_formations(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    formations = ambient[0].formations.all()
    return render(request, "AllokAcads/ambient_formations.html", {'ambient' : ambient[0], 'user' : user[0], 'formations' : formations})

def ambient_create_formations(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_create_formations.html", {'ambient' : ambient[0], 'user' : user[0]})

def ambient_create_formations_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    ambient_instance = Ambient.objects.get(ambientid = ambientid)

    name = request.POST.get('name')    
    formation = Formation(name=name)
    if formation:
        formation.save()
        ambient_instance.formations.add(formation)
    return redirect(f'/AllokAcad/ambient/resources/formations/{ambient[0].ambientid}/{user[0].userid}')

def ambient_admtypes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    admtypes = ambient[0].admin_types.all()
    return render(request, "AllokAcads/ambient_admtypes.html", {'ambient' : ambient[0], 'user' : user[0], 'admtypes' : admtypes})

def ambient_create_admtypes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_create_admtypes.html", {'ambient' : ambient[0], 'user' : user[0]})

def ambient_create_admtypes_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
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

    return render(request, "AllokAcads/ambient_create_admtypes.html", {'ambient' : ambient[0], 'user' : user[0]})

def ambient_profile_edit(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    
    if ambient.exists() and user.exists():
        ambient = ambient[0]
        user = user[0]
        username = user.name
        formations = ambient.formations.all()
        
        context = {
            'ambient': ambient,
            'user': user,
            'userid': userid,
            'username': username,
            'formations': formations
        }
        
        return render(request, "AllokAcads/ambient_profile_edit.html", context)
    else:
        return redirect('login')

def ambient_profile_edit_validate(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    member = ambient[0].members.get(user = user[0])
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
            member_formation = Member_Formation(formation=formation, formation_degree = career_level, didactic_experience_time = didatic_experience_time, professional_experience_time = professional_experience_time)
            member_formation.save()
            member.formations.add(member_formation)
    if time_in_campus:
        member.time_in_campus = time_in_campus
    if time_in_institution:
        member.time_in_institution = time_in_institution
    member.save()
    return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient[0], 'user': user[0]})

def profile(request, userid):
    user = User.objects.filter(userid = userid)
    userid = user[0].userid
    picture = user[0].picture
    return render(request, "AllokAcads/profile.html", {'userid' : userid, 'user' : user[0], 'picture' : picture})

def profile_edit(request, userid):
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/profile_edit.html", {'userid' : userid})

def profile_edit_validate(request, userid):
    user = User.objects.get(userid = userid)
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
    return redirect(f'/AllokAcad/home/profile/{user.userid}')

def enter_ambient(request, userid):
    ambientid = request.POST.get('ambient_identificator')
    ambient = Ambient.objects.get(ambientid = ambientid)
    if ambient:
        ambient.enter_solicitations.append(userid)
        ambient.save()
    return redirect(f'/AllokAcad/home/{userid}')

def professor_true(request, ambientid, userid):
    user = User.objects.get(userid = userid)
    member = Member.objects.get(user=user)
    member.is_professor = True
    member.save()
    return redirect(f'/AllokAcad/ambient/members/{ambientid}/{userid}')

def professor_false(request, ambientid, userid):
    user = User.objects.get(userid = userid)
    member = Member.objects.get(user=user)
    member.is_professor = False
    member.save()
    return redirect(f'/AllokAcad/ambient/members/{ambientid}/{userid}')

def change_position(request, memberid, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
    user = User.objects.get(userid = memberid)
    member = Member.objects.get(user=user)
    admtypes = ambient.admin_types.all()
    return render(request, "AllokAcads/change_position.html", {'ambient' : ambient, 'member' : member, 'user' : user, 'admtypes' : admtypes})

def change_position_validate(request, memberid, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
    user = User.objects.get(userid = memberid)
    member = Member.objects.get(user=user)
    admtype = AdminTP.objects.get(id=request.POST.get('admtype'))
    member.admin_type = admtype
    member.save()
    return redirect(f'/AllokAcad/ambient/members/{ambientid}/{userid}')

def run_atribuition(request, ambientid, userid):   
    ambient = Ambient.objects.get(ambientid = ambientid)
    ambient.activities.all().delete()
    ambient.activities.clear()
    ambient.save()
    user = User.objects.get(userid = userid)
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
            if subjects_rooms.filter(classroom__name = room.classroom.name).exists():
                subject_room = subjects_rooms.get(classroom__name = room.classroom.name)
                weight = room.classroom_weight + subject_room.classroom_weight
            else:
                weight = room.classroom_weight
            if weight > highest_weight and room.classroom.classroom_capacity >= activitie.tclass.number_of_students:
                highest_weight = weight
                chosen_room = room.classroom  
        for room in subjects_rooms:
            weight = room.classroom_weight
            if weight >= highest_weight and room.classroom.classroom_capacity >= activitie.tclass.number_of_students:
                highest_weight = weight
                chosen_room = room.classroom
        if(highest_weight > 0 and chosen_room != None):
            activitie.tclassroom = chosen_room
            activitie.classroom_weight = highest_weight
            activitie.save()
            chosen_room.num_uses += 1
            chosen_room.save()
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
                    if second_subjects_rooms.filter(classroom__name = room.classroom.name).exists():
                        subject_room = second_subjects_rooms.get(classroom__name = room.classroom.name)
                        weight = room.classroom_weight + subject_room.classroom_weight
                    else:
                        weight = room.classroom_weight
                    if weight > highest_weight and activitie.tclassroom.num_uses - room.classroom.num_uses >= 2 and room.classroom.classroom_capacity >= activitie.tclass.number_of_students:
                        highest_weight = weight
                        chosen_room = room.classroom
                for room in second_subjects_rooms:
                    weight = room.classroom_weight
                    if weight >= highest_weight and activitie.tclassroom.num_uses - room.classroom.num_uses >= 2 and room.classroom.classroom_capacity >= activitie.tclass.number_of_students:
                        highest_weight = weight
                        chosen_room = room.classroom
                if(highest_weight > 0 and chosen_room != None):
                    classroom_save = activitie.tclassroom
                    classroom_save.num_uses -= 1
                    activitie.tclassroom = chosen_room
                    activitie.classroom_weight = highest_weight
                    chosen_room.num_uses += 1
                    chosen_room.save()
                    classroom_save.save()
                    activitie.save()
                elif activitie.classroom_weight < 100:
                    chosen_room = None
                    similar_rooms = Classroom.objects.filter(classroom_type = activitie.tclassroom.classroom_type)
                    for room in similar_rooms:
                        if activitie.tclassroom.num_uses - room.num_uses >= 2 and room.classroom_capacity >= activitie.tclass.number_of_students:
                            chosen_room = room
                    if chosen_room:
                        classroom_save = activitie.tclassroom
                        classroom_save.num_uses -= 1
                        activitie.tclassroom = chosen_room
                        activitie.classroom_weight = highest_weight
                        chosen_room.num_uses += 1
                        chosen_room.save()
                        classroom_save.save()
                        activitie.save()

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
                    preference1 = professor.professor.prefered_classrooms.all().aggregate(total=Sum('classroom_weight'))['total'] or 0.0 + professor.professor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0 + professor.professor.prefered_classes.all().aggregate(total=Sum('class_weight'))['total'] or 0.0
                    preference2 = smallest_weight.tprofessor.prefered_classrooms.all().aggregate(total=Sum('classroom_weight'))['total'] or 0.0 + smallest_weight.tprofessor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0 + smallest_weight.tprofessor.prefered_classes.all().aggregate(total=Sum('class_weight'))['total'] or 0.0
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
                    if activitie.tclass.favorite_professors.all().filter(professor = professor):
                        tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = professor):
                        tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                        tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                        tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    for formation in relevant_formations:
                        for a_formation in formations_1:
                            if a_formation.formation == formation:
                                professional_experience_1_count = formation.professional_experience_time
                                didatic_experience_1_count = formation.didatic_experience_time
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                    if professor.time_in_campus > chosen_professor.time_in_campus:
                                        highest_weight = weight
                                        if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                            subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                        if(professor.professor_weight != 0 and subject_professor != 0):
                                            chosen_professor = professor.professor
                                            swap = 0
                                            swapAct = None
                                    elif professor.time_in_campus == chosen_professor.time_in_campus:
                                        if professor.time_in_institution > chosen_professor.time_in_institution:
                                            highest_weight = weight
                                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                            if(professor.professor_weight != 0 and subject_professor != 0):
                                                chosen_professor = professor.professor
                                                swap = 0
                                                swapAct = None
                                        elif professor.time_in_institution == chosen_professor.time_in_institution:
                                            if datetime.date.today() - professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                highest_weight = weight
                                                if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                    subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                if(professor.professor_weight != 0 and subject_professor != 0):
                                                    chosen_professor = professor.professor
                                                    swap = 0
                                                    swapAct = None
                                            elif datetime.date.today() - professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
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
                    if activitie.tclass.favorite_professors.all().filter(professor = professor):
                        tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = professor):
                        tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                        tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                        tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    for formation in relevant_formations:
                        for a_formation in formations_1:
                            if a_formation.formation == formation:
                                professional_experience_1_count = formation.professional_experience_time
                                didatic_experience_1_count = formation.didatic_experience_time
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                    if professor.time_in_campus > chosen_professor.time_in_campus:
                                        if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                            subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                        if(professor.professor_weight != 0 and subject_professor != 0):
                                            highest_weight = weight
                                            chosen_professor = professor.professor
                                            swap = 1
                                            swapAct = smallest_weight
                                    elif professor.time_in_campus == chosen_professor.time_in_campus:
                                        if professor.time_in_institution > chosen_professor.time_in_institution:
                                            if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                            if(professor.professor_weight != 0 and subject_professor != 0):
                                                highest_weight = weight
                                                chosen_professor = professor.professor
                                                swap = 1
                                                swapAct = smallest_weight
                                        elif professor.time_in_institution == chosen_professor.time_in_institution:
                                            if datetime.date.today() - professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                if subjects_professors.filter(professor__user__userid = professor.professor.user.userid).exists():
                                                    subject_professor = subjects_professors.get(professor__user__userid = professor.professor.user.userid).professor_weight
                                                if(professor.professor_weight != 0 and subject_professor != 0):
                                                    highest_weight = weight
                                                    chosen_professor = professor.professor
                                                    swap = 1
                                                    swapAct = smallest_weight
                                            elif datetime.date.today() - professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
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
                    preference1 = professor.professor.prefered_classrooms.all().aggregate(total=Sum('classroom_weight'))['total'] or 0.0 + professor.professor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0 + professor.professor.prefered_classes.all().aggregate(total=Sum('class_weight'))['total'] or 0.0
                    preference2 = smallest_weight.tprofessor.prefered_classrooms.all().aggregate(total=Sum('classroom_weight'))['total'] or 0.0 + smallest_weight.tprofessor.prefered_subjects.all().aggregate(total=Sum('subject_weight'))['total'] or 0.0 + smallest_weight.tprofessor.prefered_classes.all().aggregate(total=Sum('class_weight'))['total'] or 0.0
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
                    if activitie.tclass.favorite_professors.all().filter(professor = professor):
                        tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = professor):
                        tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                        tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                        tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    for formation in relevant_formations:
                        for a_formation in formations_1:
                            if a_formation.formation == formation:
                                professional_experience_1_count = formation.professional_experience_time
                                didatic_experience_1_count = formation.didatic_experience_time
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                    if professor.time_in_campus > chosen_professor.time_in_campus:
                                        if(professor.professor_weight != 0):
                                            highest_weight = weight
                                            chosen_professor = professor.professor
                                            swap = 0
                                            swapAct = None
                                    elif professor.time_in_campus == chosen_professor.time_in_campus:
                                        if professor.time_in_institution > chosen_professor.time_in_institution:
                                            if(professor.professor_weight != 0):
                                                highest_weight = weight
                                                chosen_professor = professor.professor
                                                swap = 0
                                                swapAct = None
                                        elif professor.time_in_institution == chosen_professor.time_in_institution:
                                            if datetime.date.today() - professor.user.birthdate > datetime.date.today() - chosen_professor.user.birthdate:
                                                if(professor.professor_weight != 0):
                                                    highest_weight = weight
                                                    chosen_professor = professor.professor
                                                    swap = 0
                                                    swapAct = None
                                            elif datetime.date.today() - professor.user.birthdate == datetime.date.today() - chosen_professor.user.birthdate:
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
                    if activitie.tclass.favorite_professors.all().filter(professor = professor):
                        tclassrooms_professor1 = activitie.tclass.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = professor):
                        tsubjects_professor1 = activitie.tsubject.favorite_professors.all().get(professor = professor).professor_weight
                    if activitie.tclass.favorite_professors.all().filter(professor = chosen_professor):
                        tclassrooms_professor2 = activitie.tclass.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    if activitie.tsubject.favorite_professors.all().filter(professor = chosen_professor):
                        tsubjects_professor2 = activitie.tsubject.favorite_professors.all().get(professor = chosen_professor).professor_weight
                    for formation in relevant_formations:
                        for a_formation in formations_1:
                            if a_formation.formation == formation:
                                professional_experience_1_count = formation.professional_experience_time
                                didatic_experience_1_count = formation.didatic_experience_time
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                    if professor.professor.time_in_campus > chosen_professor.time_in_campus:
                                        if(professor.professor_weight != 0):
                                            highest_weight = weight
                                            chosen_professor = professor.professor
                                            swap = 1
                                            swapAct = smallest_weight
                                    elif professor.professor.time_in_campus == chosen_professor.time_in_campus:
                                        if professor.professor.time_in_institution > chosen_professor.time_in_institution:
                                            if(professor.professor_weight != 0):
                                                highest_weight = weight
                                                chosen_professor = professor.professor
                                                swap = 1
                                                swapAct = smallest_weight
                                        elif professor.professor.time_in_institution == chosen_professor.time_in_institution:
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
            if swap:
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
        available_professors = 1
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
                                if a_formation.formation_degree == 'Tecnólogo':
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
                                if a_formation.formation_degree == 'Tecnólogo':
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
                activities_with_subject = sorted(activities_with_subject, key=lambda subject_activitie: sum(1 for schedule in subject_activitie.tclass.prefered_schedules if chosen_professor.prefered_schedules.filter(id=schedule.id)), reverse=True)
                for subject_activitie in activities_with_subject:
                    subject_preference = 1
                    class_preference = 1
                    if not(subject_activitie.tprofessor):
                        if chosen_professor.num_uses + subject_activitie.tclass.necessary_subjects.get(subject = subject_activitie.tsubject).periods <= ambient.max_actv_in_cicle:
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
                                    if a_formation.formation_degree == 'Tecnólogo':
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
                                    if a_formation.formation_degree == 'Tecnólogo':
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
                    if num_uses == chosen_professor.num_uses:
                        available_professors.remove(chosen_professor)
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
                    if candidate.formation.formation_degree == 'Tecnólogo':
                        degree = 25
                    elif candidate.formation.formation_degree == 'Mestre':
                        degree = 50
                    elif candidate.formation.formation.formation_degree == 'Doutor':
                        degree = 100
                    degree = a_formation.formation_weight * degree
                    if (tclassrooms_professor1 + tsubjects_professor1 > tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                        if subject_preference != 0 and class_preference != 0:
                            highest_weight = weight
                            chosen_professor = professor
                    elif (tclassrooms_professor1 + tsubjects_professor1 == tclassrooms_professor2 + tsubjects_professor2) or ((tclassrooms_professor2 < 100 and tsubjects_professor2 < 100) and (tclassrooms_professor1 == 100 or tsubjects_professor1 == 100)):
                        if degree > highest_formation:
                            if subject_preference != 0 and class_preference != 0:
                                highest_formation = degree
                                chosen_professor = candidate
                        elif degree == highest_formation:
                            if candidate.formation.professional_experience_time > highest_professional_time:
                                if subject_preference != 0 and class_preference != 0:
                                    highest_professional_time = candidate.formation.professional_experience_time
                                    chosen_professor = candidate
                            elif candidate.formation.professional_experience_time == highest_professional_time:
                                if candidate.formation.didatic_experience_time > highest_didatic_time:
                                    if subject_preference != 0 and class_preference != 0:
                                        highest_didatic_time = candidate.formation.professional_didatic_time
                                        chosen_professor = candidate
                                elif didatic_experience_1_count == didatic_experience_2_count:
                                    if candidate.time_in_campus > chosen_professor.tprofessor.time_in_campus:
                                        if subject_preference != 0 and class_preference != 0:
                                            highest_didatic_time = candidate.formation.professional_didatic_time
                                            chosen_professor = candidate
                                    elif candidate.time_in_campus == chosen_professor.tprofessor.time_in_campus:
                                        if candidate.time_in_institution > chosen_professor.tprofessor.time_in_institution:
                                            if subject_preference != 0 and class_preference != 0:
                                                highest_didatic_time = candidate.formation.professional_didatic_time
                                                chosen_professor = candidate
                                        elif candidate.time_in_institution == chosen_professor.tprofessor.time_in_institution:
                                            if datetime.date.today() - candidate.user.birthdate > datetime.date.today() - chosen_professor.tprofessor.user.birthdate:
                                                if subject_preference != 0 and class_preference != 0:
                                                    highest_didatic_time = candidate.formation.professional_didatic_time
                                                    chosen_professor = candidate
                                            elif datetime.date.today() - candidate.user.birthdate == datetime.date.today() - chosen_professor.tprofessor.user.birthdate:
                                                if formation_1_count > formation_2_count:
                                                    if subject_preference != 0 and class_preference != 0:
                                                        highest_didatic_time = candidate.formation.professional_didatic_time
                                                        chosen_professor = candidate
                            
        if chosen_professor:
            activitie_ahead_user.tprofessor = chosen_professor
            activitie_ahead_user.professor_weight = highest_weight
            activitie_ahead_user.save()
            chosen_professor.num_uses += activitie.tclass.necessary_subjects.get(subject = not_atribuited_activitie.tsubject).periods
            chosen_professor.save()

    #garante que as atividades restantes sejam atribuídas a quem deve ser

    users = ambient.members.all().filter(is_professor = True)
    average_use = 0
    if users:
        for user in users:
            average_use += user.num_uses
        average_use = average_use / len(users)
        not_atribuited_activities = ambient.activities.all().filter(tprofessor = None)
        ahead_users = []
        above_users = []
        for user in users:
            if user.num_uses > average_use:
                ahead_users.append(user)
            if user.num_uses < average_use:
                above_users.append(user)
        above_users = sorted(above_users, key=lambda x: x.num_uses)
        ahead_users = sorted(ahead_users, key=lambda x: x.num_uses, reverse=True)
        for user in above_users:
            not_atribuited_activities = ambient.activities.all().filter(tprofessor = None)
            if user.num_uses < average_use:
                if not_atribuited_activities:
                    for not_atribuited_activitie in not_atribuited_activities:
                        if not_atribuited_activitie.tsubject.favorite_professors.all().filter(professor = user):
                            subject_preference = not_atribuited_activitie.tsubject.favorite_professors.all().get(professor = user).professor_weight
                        if not_atribuited_activitie.tclass.favorite_professors.all().filter(professor = user):
                            class_preference = not_atribuited_activitie.tclass.favorite_professors.all().get(professor = user).professor_weight
                        if user.num_uses < average_use and user.num_uses + not_atribuited_activitie.tclass.necessary_subjects.get(subject = not_atribuited_activitie.tsubject).periods <= ambient.max_actv_in_cicle:
                            if subject_preference != 0 and class_preference != 0:
                                not_atribuited_activitie.tprofessor = user
                                not_atribuited_activitie.professor_weight = 0
                                user.num_uses += activitie.tclass.necessary_subjects.get(subject = activitie.tsubject).periods
                                not_atribuited_activitie.save()
                                user.save()
                elif ahead_users:
                    ahead_users = sorted(ahead_users, key=lambda ahead_user: ahead_user.num_uses, reverse=True)
                    for ahead_user in ahead_users:
                        activities_ahead_users = ambient.activities.filter(tprofessor = ahead_user).order_by("professor_weight")
                        for activitie_ahead_user in activities_ahead_users:
                            if user.num_uses < average_use and ahead_user.num_uses > average_use and user.num_uses + activitie_ahead_user.tclass.necessary_subjects.get(subject = activitie_ahead_user.tsubject).periods <= ambient.max_actv_in_cicle:
                                current_preference_class = 100
                                current_preference_subject = 100
                                if activitie_ahead_user.tsubject.favorite_professors.filter(professor = activitie_ahead_user.tprofessor):
                                    current_preference_subject = activitie_ahead_user.tsubject.favorite_professors.get(professor = activitie_ahead_user.tprofessor).professor_weight
                                if activitie_ahead_user.tclass.favorite_professors.filter(professor = activitie_ahead_user.tprofessor):
                                    current_preference_class = activitie_ahead_user.tclass.favorite_professors.get(professor = activitie_ahead_user.tprofessor).professor_weight
                                if current_preference_subject < 100 and current_preference_class < 100:
                                    if activitie_ahead_user.tsubject.favorite_professors.all().filter(professor = user):
                                        subject_preference = activitie_ahead_user.tsubject.favorite_professors.all().get(professor = user)
                                    if activitie_ahead_user.tclass.favorite_professors.all().filter(professor = user):
                                        class_preference = activitie_ahead_user.tclass.favorite_professors.all().get(professor = user)
                                    if subject_preference != 0 and class_preference != 0:
                                        activitie_ahead_user.tprofessor = user
                                        activitie.professor_weight = 0
                                        activitie_ahead_user.save()
                                        user.num_uses += activitie.tclass.necessary_subjects.get(subject = activitie_ahead_user.tsubject).period
                                        ahead_user.num_uses -= activitie.tclass.necessary_subjects.get(subject = activitie_ahead_user.tsubject).periods
        #aqui, trata de atribuir materias restantes aos usuarios que tem falta delas

    return redirect(f'/AllokAcad/ambient/{ambientid}/{userid}')

def run_alocation(request, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
    timetable = Timetable(lines_number = ambient.periods_in_a_day, column_number = ambient.days_in_a_cicle)
    ambient.published_timetable = timetable
    ambient.save()
    for schedule in ambient.available_schedules.all():
        alocation = Alocation(line = schedule.column, column = schedule.line)
        ambient.published_timetable.table.add(alocation)
        ambient.save()
    activities = ambient.activities.all()
    swap = True
    while(swap):
        swap = False
        for activitie in activities:
            highest_weight = 0
            chosen_sch = None
            for schedule_c in activitie.tclass.prefered_schedules:
                line = schedule_c.line
                column = schedule_c.column
                weight = 0
                for i in range(activitie.activities_qtd):
                    if activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i):
                        if not ambient.published_timetable.table.all().get(line = column+i, column = line).activitie:
                            ambient_sch = activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i)
                            weight += 1
                            if activitie.tprofessor.prefered_schedules.all().filter(id = ambient_sch.id):
                                weight += 1
                        else:
                            p_weight = 0
                            p_ambient_sch = 0
                            for i in range(activitie.activities_qtd):
                                if activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i):
                                    if not ambient.published_timetable.table.all().get(line = column+i, column = line).activitie:
                                        p_ambient_sch = activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i)
                                        p_weight += 1
                                        if activitie.tprofessor.prefered_schedules.all().filter(id = p_ambient_sch.id):
                                            p_weight += 1

                            t_weight = 0
                            t_ambient_sch = 0
                            t_activitie = ambient.published_timetable.table.all().get(line = column+i, column = line).activitie
                            for i in range(t_activitie.activities_qtd):
                                if t_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i):
                                    t_ambient_sch = t_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i)
                                    t_weight += 1
                                    if t_activitie.tprofessor.prefered_schedules.all().filter(id = t_ambient_sch.id):
                                        t_weight += 1
                            
                            if p_weight > t_weight:
                                swap = True
                                weight = p_weight
                                chosen_sch = schedule_c
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

            if highest_weight and chosen_sch:
                for i in range(activitie.activities_qtd.qtd):
                    t_alocation = ambient.published_timetable.table.all().get(line = chosen_sch.column+i, column = chosen_sch.line)
                    t_alocation.activitie = activitie
                    t_alocation.save()

    for activitie in activities:
        not_alocated_activities = []
        if not ambient.published_timetable.table.all().filter(activitie = activitie):
            not_alocated_activities.append(activitie)

        
    while(swap):
            swap = False
            for not_alocated_activitie in not_alocated_activities:
                highest_weight = 0
                chosen_sch = None
                if not not_alocated_activitie.tclass.prefered_schedules and not_alocated_activitie.tprofessor.prefered_schedules:
                    for schedule_c in not_alocated_activitie.tprofessor.prefered_schedules:
                        line = schedule_c.line
                        column = schedule_c.column
                        weight = 0        
                        for i in range(not_alocated_activitie.activities_qtd):
                            if not_alocated_activitie.tprofessor.prefered_schedules.all().filter(line=line, column=column+i):
                                if not ambient.published_timetable.table.all().get(line = column+i, column = line).activitie:
                                    weight += 1
                                else:
                                    #criterio de desempate
                                    weight = 0
                                    break
                            else:
                                weight = 0
                                break
                else:
                    p_weight = 0
                    p_ambient_sch = 0
                    for i in range(not_alocated_activitie.activities_qtd):
                        if not_alocated_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i):
                            if not ambient.published_timetable.table.all().get(line = column+i, column = line).activitie:
                                p_ambient_sch = activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i)
                                p_weight += 1
                                if not_alocated_activitie.tprofessor.prefered_schedules.all().filter(id = p_ambient_sch.id):
                                    p_weight += 1

                    t_weight = 0
                    t_ambient_sch = 0
                    t_activitie = ambient.published_timetable.table.all().get(line = column+i, column = line).activitie
                    for i in range(t_activitie.activities_qtd):
                        if t_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i):
                            t_ambient_sch = t_activitie.tclass.prefered_schedules.all().filter(line=line, column=column+i)
                            t_weight += 1
                            if t_activitie.tprofessor.prefered_schedules.all().filter(id = t_ambient_sch.id):
                                t_weight += 1

                    if p_weight > t_weight:
                        swap = True
                        weight = p_weight
                        chosen_sch = schedule_c
                        break
                    else:
                        weight = 0
                        break
                
                if highest_weight and chosen_sch:
                        for i in range(not_alocated_activitie.activities_qtd):
                            t_alocation = ambient.published_timetable.table.all().get(line = chosen_sch.column+i, column = chosen_sch.line)
                            t_alocation.activitie = activitie
                            t_alocation.save()
    return redirect(f'/AllokAcad/ambient/{ambientid}/{userid}')