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

class Invitation(models.Model):
    inviting_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='inviting_user')
    invited_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='invited_user')
    status = models.BooleanField(default=False)

class Member(models.Model):
    registration = models.CharField(max_length=40)
    formations = models.ManyToManyField('Formation')
    professional_experience_time = ArrayField(models.IntegerField())
    didactic_experience_time = ArrayField(models.IntegerField())
    time_in_campus = ArrayField(models.IntegerField())
    time_in_institution = ArrayField(models.IntegerField())
    career_level = models.CharField(max_length=40)
    admin_type = models.ForeignKey('AdminTP', on_delete=models.CASCADE)
    is_professor = models.BooleanField(default=False)
    max_actv_in_cicle = models.IntegerField()
    min_actv_in_cicle = models.IntegerField()
    max_actv_in_day = models.IntegerField()
    min_actv_in_day = models.IntegerField()
    prefered_schedules = ArrayField(ArrayField(models.IntegerField()))
    schedule_weight = ArrayField(models.FloatField())
    prefered_classes = models.ManyToManyField('Class')
    classes_weight = ArrayField(models.FloatField())
    prefered_classrooms = models.ManyToManyField('Classroom')
    classrooms_weight = ArrayField(models.FloatField())
    prefered_subjects = models.ManyToManyField('Subject')
    subjects_weight = ArrayField(models.FloatField())
    num_uses = models.IntegerField()

class AdminTP(models.Model):
    name = models.CharField(max_length=40)
    can_configure_ambient = models.BooleanField()
    can_gerenciate_members = models.BooleanField()
    can_register_resources = models.BooleanField()
    can_run_atribuition = models.BooleanField()
    can_run_alocation = models.BooleanField()
    can_delete_ambient = models.BooleanField()

class Class(models.Model):
    name = models.CharField(max_length=40)
    prefered_schedules = ArrayField(ArrayField(models.IntegerField()))
    ideal_classrooms = models.ManyToManyField('Classroom')   
    classrooms_weight = ArrayField(models.FloatField())
    necessary_subjects = models.ManyToManyField('Subject')
    favorite_professors = models.ManyToManyField('Member')
    professors_weight = ArrayField(models.FloatField())
    periods_per_subjtect = ArrayField(models.IntegerField())
    number_of_students = models.IntegerField()
    num_uses = models.IntegerField()

class Classroom(models.Model):
    name = models.CharField(max_length=40)
    available_schedules = ArrayField(ArrayField(models.IntegerField()))
    classroom_type = models.ForeignKey('ClassroomTP', on_delete=models.CASCADE)
    classroom_capacity = models.IntegerField()
    num_uses = models.IntegerField()

class ClassroomTP(models.Model):
    name = models.CharField(max_length=40)
    num_uses = models.IntegerField()

class Subject(models.Model):
    name = models.CharField(max_length=40)
    ideal_classrooms = models.ManyToManyField('Classroom')
    classrooms_weight = ArrayField(models.FloatField())
    favorite_professors = models.ManyToManyField('Member')
    professors_weight = ArrayField(models.FloatField())
    relevant_formations = models.ManyToManyField('Formation')
    formations_weight = ArrayField(models.FloatField())
    num_uses = models.IntegerField()

class Ambient(models.Model):
    ID = models.CharField(max_length=9)
    name = models.CharField(max_length=60)
    picture = models.ImageField()
    description = models.TextField(max_length=500)
    periods_in_a_day = models.IntegerField()
    days_ins_a_cicle = models.IntegerField()
    breaks = ArrayField(ArrayField(models.IntegerField()))
    enter_alt_solicitations = ArrayField(models.CharField())
    form_opening = models.DateField()
    form_closing = models.DateField()
    alt_solicitations_opening = models.DateField()
    alt_solicitations_closing = models.DateField()
    max_actv_in_cicle = models.IntegerField()
    min_actv_in_cicle = models.IntegerField()
    max_actv_in_day = models.IntegerField()
    min_actv_in_day = models.IntegerField()
    members = models.ManyToManyField('Member', related_name='members')
    formations = models.ManyToManyField('Formation')
    classes = models.ManyToManyField('Class')
    classrooms = models.ManyToManyField('Classroom')
    professors = models.ManyToManyField('Member', related_name='professors')
    subjects = models.ManyToManyField('Subject')
    activities = models.ManyToManyField('Activitie')
    published_timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE, related_name='published_timetable')
    edit_timetable = models.ForeignKey('Timetable', on_delete=models.CASCADE, related_name='edit_timetable')

class Formation(models.Model):
    name = models.CharField(max_length=40)
    num_uses = models.IntegerField()

class Activitie(models.Model):
    tclass = models.ForeignKey('Class', on_delete=models.CASCADE)
    tclassroom = models.ForeignKey('Classroom', on_delete=models.CASCADE)
    tprofessor = models.ForeignKey('Member', on_delete=models.CASCADE)
    tsubject = models.ForeignKey('Subject', on_delete=models.CASCADE)

class Timetable(models.Model):
    lines = models.IntegerField()
    columns = models.IntegerField()
    table = ArrayField(ArrayField(models.IntegerField()))
    available_spaces = ArrayField(ArrayField(models.IntegerField()))
    available_activities = models.ManyToManyField('Activitie', related_name='available_activities')
    not_atribuited = models.ManyToManyField('Activitie', related_name='not_atribuited')
    alt_solicitations = ArrayField(models.TextField(max_length=500))
    quality_rate = models.FloatField()
