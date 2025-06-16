from django.db import models

class Semester(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete=models.CASCADE, related_name="semesters")
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ('ambient', 'name')

class ProfessorStatisticsDay(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    professor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE)
    timetable = models.ForeignKey('AllokAcads.Timetable', on_delete = models.CASCADE)
    
    day = models.IntegerField()
    semester = models.CharField(max_length = 100)
    
    periods_on_campus = models.IntegerField(default=0)
    periods_interval = models.IntegerField(default=0) 
    number_of_periods = models.IntegerField(default=0)
    
    day_efficiency = models.FloatField(default=0.0)
    trips_to_campus = models.IntegerField(default=0)
    
    create_at = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ('professor', 'day', 'timetable')
        

    

    
    
    
    
