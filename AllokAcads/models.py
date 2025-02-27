from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.

class User(models.Model):
    ID = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=80)
    email = models.EmailField(max_length=20)
    birthdate = models.DateField()
    password = models.CharField(max_length=20)
    description = models.TextField(max_length=500)
    picture = models.ImageField()
    invitations = models.ManyToManyField('Invitation')
    ambients = models.ManyToManyField('Ambient')

class Member(models.Model):
    registration = models.CharField(max_length=40)
    formations = models.ManyToManyField('Member_Formation')
    time_in_campus = ArrayField(models.IntegerField())
    time_in_institution = ArrayField(models.IntegerField())
    career_level = models.CharField(max_length=40)
    admin_type = models.ForeignKey('AdminTP', on_delete=models.CASCADE)
    is_professor = models.BooleanField(default=False)
    max_actv_in_cicle = models.IntegerField()
    min_actv_in_cicle = models.IntegerField()
    max_actv_in_day = models.IntegerField()
    min_actv_in_day = models.IntegerField()
    prefered_schedules = models.ManyToManyField('Schedule_Preference')
    prefered_classes = models.ManyToManyField('Class_Preference')
    prefered_classrooms = models.ManyToManyField('Classroom_Preference')
    prefered_subjects = models.ManyToManyField('Subject_Preference')
    subjects_weight = ArrayField(models.FloatField())
    num_uses = models.IntegerField()

class Class(models.Model):
    name = models.CharField(max_length=40)
    prefered_schedules = models.ManyToManyField('Schedule_Preference')
    ideal_classrooms = models.ManyToManyField('Classroom_Preference')
    necessary_subjects = models.ManyToManyField('Subject')
    favorite_professors = models.ManyToManyField('Professor_Preference')
    number_of_students = models.IntegerField()
    num_uses = models.IntegerField()

class Classroom(models.Model):
    name = models.CharField(max_length=40)
    prefered_schedules = models.ManyToManyField('Schedule_Preference')
    classroom_type = models.ForeignKey('ClassroomTP', on_delete=models.CASCADE)
    classroom_capacity = models.IntegerField()
    num_uses = models.IntegerField()

class Subject(models.Model):
    name = models.CharField(max_length=40)
    ideal_classrooms = models.ManyToManyField('Classroom_Preference')
    favorite_professors = models.ManyToManyField('Professor_Preference')
    relevant_formations = models.ManyToManyField('Formation_Preference')
    num_uses = models.IntegerField()

class Ambient(models.Model):
    ID = models.CharField(max_length=9)
    name = models.CharField(max_length=60)
    picture = models.ImageField()
    description = models.TextField(max_length=500)
    periods_in_a_day = models.IntegerField()
    days_ins_a_cicle = models.IntegerField()
    breaks = ArrayField(ArrayField(models.IntegerField()))
    enter_solicitations = ArrayField(models.CharField(max_length=9))
    form_opening = models.DateField()
    form_closing = models.DateField()
    alt_solicitations_opening = models.DateField()
    alt_solicitations_closing = models.DateField()
    max_actv_in_cicle = models.IntegerField()
    min_actv_in_cicle = models.IntegerField()
    max_actv_in_day = models.IntegerField()
    min_actv_in_day = models.IntegerField()
    members = models.ManyToManyField('Member')
    formations = models.ManyToManyField('Formation')
    classes = models.ManyToManyField('Class')
    classrooms = models.ManyToManyField('Classroom')
    subjects = models.ManyToManyField('Subject')
    activities = models.ManyToManyField('Activitie')
    published_timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE, related_name='published_timetable')
    edit_timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE, related_name='edit_timetable')

class AdminTP(models.Model):
    name = models.CharField(max_length=40)
    can_configure_ambient = models.BooleanField()
    can_gerenciate_members = models.BooleanField()
    can_register_resources = models.BooleanField()
    can_run_atribuition = models.BooleanField()
    can_run_alocation = models.BooleanField()
    
class ClassroomTP(models.Model):
    name = models.CharField(max_length=40)
    num_uses = models.IntegerField()

class Formation(models.Model):
    name = models.CharField(max_length=40)
    num_uses = models.IntegerField()

class Activitie(models.Model):
    tclass = models.ForeignKey('Class', on_delete=models.CASCADE)
    tclassroom = models.ForeignKey('Classroom', on_delete=models.CASCADE)
    tprofessor = models.ForeignKey('Member', on_delete=models.CASCADE)
    tsubject = models.ForeignKey('Subject', on_delete=models.CASCADE)

class Timetable(models.Model):
    lines_number = models.IntegerField()
    columns_number = models.IntegerField()
    table = models.ManyToManyField('Alocation')
    not_alocated = models.ManyToManyField('Unregistered_Activitie', related_name='not_alocated')
    not_atribuited = models.ManyToManyField('Unregistered_Activitie', related_name='not_atribuited')
    alt_solicitations = ArrayField(models.TextField(max_length=500))
    quality_rate = models.FloatField()

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