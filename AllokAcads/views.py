from django.shortcuts import render, redirect
from django.conf import settings
import random, os, datetime, time
from .models import User, Ambient, Member, AdminTP, ClassroomTP, Formation, Subject, Formation_Preference, Classroom, Class, Professor_Preference, Classroom_Preference, Schedule_Preference, Class_Preference, Subject_Preference, Member_Formation, Activitie, Timetable, Alocation, Unregistered_Activitie
from shutil import copyfile

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
    
    
    ordered_table = []
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
    not_alocated = ambient.published_timetable.not_alocated.all()
    
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
    user = User.objects.get(userid = userid)
    ambient = Ambient.objects.get(ambientid = ambientid)
    picture = user.picture
    return render(request, "AllokAcads/ambient_profile.html", {'user' : user, 'ambient' : ambient, 'picture' : picture, 'userid': userid})

def ambient_members(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    members = ambient[0].members.all()
    return render(request, "AllokAcads/ambient_members.html", {'ambient' : ambient[0], 'user' : user[0], 'members' : members, 'userid': userid})

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
    ambient = Ambient.objects.get(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    solicitations = ambient.enter_solicitations
    names = []
    for solicitation in solicitations:
        name = User.objects.get(userid = solicitation).name
        names.append(name)
    solicitations = zip(names, solicitations)
    return render(request, "AllokAcads/ambient_solicitations.html", {'solicitations' : solicitations, 'ambient' : ambient, 'user' : user[0], 'userid': userid})

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
    return redirect(f'/AllokAcad/ambient/solicitations{ambientid}/{userid}')

def ambient_resources(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid=ambientid)
    user = User.objects.filter(userid=userid)
    
    if ambient.exists() and user.exists():
        ambient = ambient[0]
        user = user[0]
        
        # Inclua username no contexto (necessário para o base.html)
        username = user.name
        
        context = {
            'ambient': ambient,
            'user': user,
            'userid': userid,  # Explicitamente passar userid
            'username': username  # Adicionar o username para o template base
        }
        
        return render(request, "AllokAcads/ambient_resources.html", context)
    else:
        return redirect('login')

def ambient_subjects(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    subjects = ambient[0].subjects.all()
    return render(request, "AllokAcads/ambient_subjects.html", {'ambient' : ambient[0], 'user' : user[0], 'subjects' : subjects, 'userid': userid})

def ambient_create_subjects(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    classrooms = ambient[0].classrooms.all()
    professors = ambient[0].members.all().filter(is_professor = True)
    formations = ambient[0].formations.all()
    return render(request, "AllokAcads/ambient_create_subjects.html", {'ambient' : ambient[0], 'user' : user[0], 'classrooms' : classrooms, 'professors' : professors, 'formations' : formations, 'userid': userid})

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
    return render(request, "AllokAcads/ambient_rooms.html", {'ambient' : ambient[0], 'user' : user[0], 'rooms' : rooms, 'userid': userid})

def ambient_create_rooms(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    roomtypes = ambient[0].classroom_types.all()
    return render(request, "AllokAcads/ambient_create_rooms.html", {'ambient' : ambient[0], 'user' : user[0], 'roomtypes' : roomtypes, 'userid': userid})

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
    return render(request, "AllokAcads/ambient_roomtypes.html", {'ambient' : ambient[0], 'user' : user[0], 'roomtypes' : roomtypes, 'userid': userid})

def ambient_create_roomtypes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_create_roomtypes.html", {'ambient' : ambient[0], 'user' : user[0], 'userid': userid})

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
    username = user[0].name
    return render(request, "AllokAcads/ambient_classes.html", {'ambient': ambient[0], 'user': user[0], 'userid': userid, 'username': username, 'classes': classes})

def ambient_create_classes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    schedules = ambient[0].available_schedules.all()
    classrooms = ambient[0].classrooms.all()
    professors = ambient[0].members.all().filter(is_professor = True)
    subjects = ambient[0].subjects.all()
    columns = ambient[0].periods_in_a_day
    username = user[0].name
    return render(request, "AllokAcads/ambient_create_classes.html", {'ambient': ambient[0], 'user': user[0], 'userid': userid, 'username': username, 'classrooms': classrooms, 'professors': professors, 'subjects': subjects, 'schedules': schedules, 'columns': columns})

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
            subject.favorite_professors.add(professor_preference)
    subject_ids = request.POST.getlist("necessary_subjects")
    if subject_ids:
        for subject_id in subject_ids:
            subject = Subject.objects.get(id = subject_id)
            tclass.necessary_subjects.add(subject)
    ambient_instance.classes.add(tclass)
    return redirect(f'/AllokAcad/ambient/resources/classes/{ambient[0].ambientid}/{user[0].userid}')

def ambient_formations(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    formations = ambient[0].formations.all()
    return render(request, "AllokAcads/ambient_formations.html", {'ambient' : ambient[0], 'user' : user[0], 'formations' : formations, 'userid': userid})

def ambient_create_formations(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_create_formations.html", {'ambient' : ambient[0], 'user' : user[0], 'userid': userid})

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
    return render(request, "AllokAcads/ambient_admtypes.html", {'ambient' : ambient[0], 'user' : user[0], 'admtypes' : admtypes, 'userid': userid})

def ambient_create_admtypes(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_create_admtypes.html", {'ambient' : ambient[0], 'user' : user[0], 'userid': userid})

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
    formations = ambient[0].formations.all()
    return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient[0], 'user': user[0], 'formations' : formations, 'userid': userid})

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
    return render(request, "AllokAcads/ambient_profile_edit.html", {'ambient': ambient[0], 'user': user[0], 'userid': userid})

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
    member = ambient.members.get(user=user)
    admtypes = ambient.admin_types.all()
    current_user = User.objects.get(userid = userid)
    return render(request, "AllokAcads/change_position.html", {'ambient' : ambient, 'member' : member, 'user' : user, 'admtypes' : admtypes, 'userid': userid})

def change_position_validate(request, memberid, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
    user = User.objects.get(userid = memberid)
    member = ambient.members.get(user=user)
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
            activitie = Activitie(tclass = aclass, tsubject = subject)
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
    return redirect(f'/AllokAcad/ambient/{ambientid}/{userid}')

def run_alocation(request, ambientid, userid):
    ambient = Ambient.objects.get(ambientid = ambientid)
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
                                        conflit = None
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
            
    for activitie in activities:
        not_alocated_activities = []
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
                                            conflit = None
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

    return redirect(f'/AllokAcad/ambient/{ambientid}/{userid}')