from django.db import models

class ProfessorDaySubject(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    professor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE)
    subject = models.ForeignKey('AllokAcads.Subject', on_delete = models.CASCADE)
    semester = models.ForeignKey('Semester', on_delete = models.CASCADE)
    
    day = models.IntegerField()
    period = models.IntegerField()
    
    class Meta: 
        unique_together = ('ambient', 'professor', 'subject', 'semester', 'day', 'period')
    
class ProfessorStatistics(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    professor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE)
    semester = models.ForeignKey('Semester', on_delete = models.CASCADE)
    
    day = models.IntegerField()
    
    periods_on_campus = models.IntegerField(default = 0)
    periods_interval = models.IntegerField(default = 0) 
    number_of_periods = models.IntegerField(default = 0)
    day_efficiency = models.FloatField(default = 0.0)
    
    create_at = models.DateField(auto_now_add = True)
    
    class Meta: 
        unique_together = ('ambient', 'professor', 'semester', 'day')

class SpaceDaySubject(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    classroom = models.ForeignKey('AllokAcads.Classroom', on_delete = models.CASCADE)
    tclass = models.ForeignKey('AllokAcads.Class', on_delete = models.CASCADE)
    subject = models.ForeignKey('AllokAcads.Subject', on_delete = models.CASCADE)
    semester = models.ForeignKey('Semester', on_delete = models.CASCADE)
    
    day = models.IntegerField()
    period = models.IntegerField()
    
    classroom_number_of_students = models.IntegerField(default = 0)
    class_number_of_students = models.IntegerField(default = 0)
    
    create_at = models.DateField(auto_now_add = True)    
    
    class Meta: 
        unique_together = ('ambient', 'classroom', 'semester', 'day', 'period')

class SpaceStatistics(models.Model): 
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE, null=True)
    classroom = models.ForeignKey('AllokAcads.Classroom', on_delete = models.CASCADE, null=True)
    semester = models.ForeignKey('Semester', on_delete = models.CASCADE, null=True)
    
    total_periods_available = models.IntegerField(default=0)
    total_periods_use = models.IntegerField(default=0)
    number_of_spaces = models.IntegerField(default=0)
    use_time_rate = models.FloatField(default=0.0)
    
    create_at = models.DateField(auto_now_add = True)
    
class Semester(models.Model):
    name = models.CharField(max_length = 100)
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    timetable = models.ForeignKey('AllokAcads.Timetable', on_delete = models.CASCADE, null = True)
    create_at = models.DateField(auto_now_add = True)
    
    is_active = models.BooleanField(default = True)
    
    class Meta: 
        unique_together = ('name', 'ambient')
        ordering = ['-create_at']
    

    
    
    
    