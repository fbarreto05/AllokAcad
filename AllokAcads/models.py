from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.

class User(models.Model):
    userid = models.CharField(max_length=9, blank=True, null=True)
    name = models.CharField(max_length=80, null=False)
    email = models.EmailField(max_length=254, null=False)
    birthdate = models.DateField(null=False)
    password = models.CharField(max_length=20, null=False)
    description = models.TextField(max_length=500, null=True)
    picture = models.ImageField(null=True)
    invitations = models.ManyToManyField('Invitation')
    ambients = models.ManyToManyField('Ambient')

class Member(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    registration = models.CharField(max_length=40, null=True)
    formations = models.ManyToManyField('Member_Formation')
    time_in_campus = ArrayField(models.IntegerField(), null=True)
    time_in_institution = ArrayField(models.IntegerField(), null=True)
    career_level = models.CharField(max_length=40, null=True)
    admin_type = models.ForeignKey('AdminTP', on_delete=models.CASCADE, null=False)
    is_professor = models.BooleanField(default=False, null=False)
    max_actv_in_cicle = models.IntegerField(null=True)
    min_actv_in_cicle = models.IntegerField(null=True)
    max_actv_in_day = models.IntegerField(null=True)
    min_actv_in_day = models.IntegerField(null=True)
    prefered_schedules = models.ManyToManyField('Schedule_Preference')
    prefered_classes = models.ManyToManyField('Class_Preference')
    prefered_classrooms = models.ManyToManyField('Classroom_Preference')
    prefered_subjects = models.ManyToManyField('Subject_Preference')
    num_uses = models.IntegerField(null=True)

class Class(models.Model):
    name = models.CharField(max_length=40)
    prefered_schedules = models.ManyToManyField('Schedule_Preference')
    ideal_classrooms = models.ManyToManyField('Classroom_Preference')
    necessary_subjects = models.ManyToManyField('Subject')
    favorite_professors = models.ManyToManyField('Professor_Preference')
    number_of_students = models.IntegerField()
    num_uses = models.IntegerField(null=True)

class Classroom(models.Model):
    name = models.CharField(max_length=40)
    classroom_type = models.ForeignKey('ClassroomTP', on_delete=models.CASCADE)
    classroom_capacity = models.IntegerField()
    num_uses = models.IntegerField(null=True)

class Subject(models.Model):
    name = models.CharField(max_length=40)
    ideal_classrooms = models.ManyToManyField('Classroom_Preference')
    favorite_professors = models.ManyToManyField('Professor_Preference')
    relevant_formations = models.ManyToManyField('Formation_Preference')
    num_uses = models.IntegerField(null=True)

def ambient_image_path(instance, filename):
    return f'ambients/{instance.ambientid}/picture/{filename}'

class Ambient(models.Model):
    ambientid = models.CharField(max_length=9, blank=True, null=True)
    name = models.CharField(max_length=60, null=False)
    picture = models.ImageField(upload_to=ambient_image_path, null=True)
    description = models.TextField(max_length=500, null=True)
    periods_in_a_day = models.IntegerField(null=True)
    days_in_a_cicle = models.IntegerField(null=True)
    available_schedules = models.ManyToManyField('Schedule_Preference')
    breaks = ArrayField(ArrayField(models.IntegerField(null=False), null=True), null=True)
    enter_solicitations = ArrayField(models.CharField(max_length=9, null=False), null=True)
    form_opening = models.DateField(null=True)
    form_closing = models.DateField(null=True)
    alt_solicitations_opening = models.DateField(null=True)
    alt_solicitations_closing = models.DateField(null=True)
    max_actv_in_cicle = models.IntegerField(null=True)
    min_actv_in_cicle = models.IntegerField(null=True)
    max_actv_in_day = models.IntegerField(null=True)
    min_actv_in_day = models.IntegerField(null=True)
    admin_types = models.ManyToManyField('AdminTP')
    members = models.ManyToManyField('Member')
    formations = models.ManyToManyField('Formation')
    classes = models.ManyToManyField('Class')
    classrooms = models.ManyToManyField('Classroom')
    classroom_types = models.ManyToManyField('ClassroomTP')
    subjects = models.ManyToManyField('Subject')
    activities = models.ManyToManyField('Activitie')
    published_timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE, related_name='published_timetable', null=True)
    edit_timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE, related_name='edit_timetable', null=True)

class AdminTP(models.Model):
    name = models.CharField(max_length=40, null=False)
    can_configure_ambient = models.BooleanField(null=False)
    can_gerenciate_members = models.BooleanField(null=False)
    can_register_resources = models.BooleanField(null=False)
    can_run_atribuition = models.BooleanField(null=False)
    can_run_alocation = models.BooleanField(null=False)
    
class ClassroomTP(models.Model):
    name = models.CharField(max_length=40)
    num_uses = models.IntegerField(null=True)

class Formation(models.Model):
    name = models.CharField(max_length=40)
    num_uses = models.IntegerField(null=True)

class Activitie(models.Model):
    tclass = models.ForeignKey('Class', on_delete=models.CASCADE)
    tclassroom = models.ForeignKey('Classroom', on_delete=models.CASCADE)
    tprofessor = models.ForeignKey('Member', on_delete=models.CASCADE)
    tsubject = models.ForeignKey('Subject', on_delete=models.CASCADE)

class Timetable(models.Model):
    lines_number = models.IntegerField(null=True)
    columns_number = models.IntegerField(null=True)
    table = models.ManyToManyField('Alocation')
    not_alocated = models.ManyToManyField('Unregistered_Activitie', related_name='not_alocated')
    not_atribuited = models.ManyToManyField('Unregistered_Activitie', related_name='not_atribuited')
    alt_solicitations = ArrayField(models.TextField(max_length=500, null=False), null=True)
    quality_rate = models.FloatField(null=True)

class Alocation(models.Model):
    line = models.IntegerField()
    column = models.IntegerField()
    Activitie = models.ForeignKey('Activitie', on_delete=models.CASCADE)

class Unregistered_Activitie(models.Model):
    activitie = models.ForeignKey('Activitie', on_delete=models.CASCADE)
    message = models.TextField(max_length=400)

class Invitation(models.Model):
    inviting_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='inviting_user')
    invited_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='invited_user')
    status = models.BooleanField(default=False)

class Member_Formation(models.Model):
    formation = models.ForeignKey('Formation', on_delete=models.CASCADE)
    professional_experience_time = models.IntegerField()
    didactic_experience_time = models.IntegerField()

class Schedule_Preference(models.Model):
    line = models.IntegerField()
    column = models.IntegerField()

class Class_Preference(models.Model):
    tclass = models.ForeignKey("Class", on_delete=models.CASCADE)
    class_weight = models.FloatField()

class Classroom_Preference(models.Model):
    classroom = models.ForeignKey("Classroom", on_delete=models.CASCADE)
    classroom_weight = models.FloatField()

class Subject_Preference(models.Model):
    subject = models.ForeignKey("Subject", on_delete=models.CASCADE)
    subject_weight = models.FloatField()
    periods = models.IntegerField()

class Professor_Preference(models.Model):
    professor = models.ForeignKey("Member", on_delete=models.CASCADE)
    professor_weight = models.FloatField()

class Formation_Preference(models.Model):
    formation = models.ForeignKey("Formation", on_delete=models.CASCADE)
    formation_weight = models.FloatField()