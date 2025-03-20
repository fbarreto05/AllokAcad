from django.shortcuts import render, redirect
import random, os
from .models import User, Ambient, Member, AdminTP, ClassroomTP, Formation, Subject, Formation_Preference, Classroom, Class, Professor_Preference, Classroom_Preference, Schedule_Preference

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

    user = User(userid=identificator, name=name, email=email, password=password, birthdate=birthdate)
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
    
    main_adm = AdminTP(name='Administrador Principal', can_configure_ambient=True, can_gerenciate_members=True, can_register_resources=True, can_run_atribuition=True, can_run_alocation=True)
    main_adm.save()
    
    user = User.objects.filter(userid = userid)

    creator = Member(user=user[0], admin_type=main_adm, is_professor=False)
    ambient = Ambient(ambientid=identificator, name=name, picture=picture, description=description)

    user[0].save()
    ambient.save()
    creator.save()

    user[0].ambients.add(ambient)
    ambient.admin_types.add(main_adm)
    ambient.members.add(creator)

    return redirect(f'/AllokAcad/home/{userid}')

def ambient(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient.html", {'ambient' : ambient[0], 'user' : user[0]})

def ambient_config(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_config.html", {'ambient' : ambient[0], 'user' : user[0]})

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
    return render(request, "AllokAcads/ambient_profile.html")

def ambient_members(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    members = ambient[0].members.all()
    return render(request, "AllokAcads/ambient_members.html", {'ambient' : ambient[0], 'user' : user[0], 'members' : members})

def ambient_form(request, ambientid, userid):
    return render(request, "AllokAcads/ambient_form.html")

def ambient_solicitations(request, ambientid, userid):
    return render(request, "AllokAcads/ambient_solicitations.html")

def ambient_resources(request, ambientid, userid):
    ambient = Ambient.objects.filter(ambientid = ambientid)
    user = User.objects.filter(userid = userid)
    return render(request, "AllokAcads/ambient_resources.html", {'ambient' : ambient[0], 'user' : user[0]})

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
            print("classroom_preference", classroom_preference)
            subject.ideal_classrooms.add(classroom_preference)
    professor_ids = request.POST.getlist("favorite_professors")
    if professor_ids:
        for professor_id in professor_ids:
            professor = Formation.objects.get(id = professor_id)
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
    room = Classroom(name=name, classroom_type=roomtype, classroom_capacity=capacity)
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
    lines = ambient[0].days_in_a_cicle
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
            professor = Formation.objects.get(id = professor_id)
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
