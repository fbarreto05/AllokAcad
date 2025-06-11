from django.db import models
from AllokAcads.models import Activitie

class ProfessorStatisticsDay(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE, null = True)
    professor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE, null = True)
    day = models.CharField()
    create_at = models.DateField(auto_now_add=True)
    semester = models.CharField(max_length = 10)
    
    hours_on_campus = models.FloatField()
    classes_hours = models.FloatField()
    trips_to_campus = models.IntegerField() 
    number_of_classes = models.IntegerField()
    classes_interval = models.FloatField()
    day_efficiency = models.FloatField()
            
class ProfessorStatisticsSemester(models.Model):
    profesor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE, null = True)
    semester = models.CharField(max_length = 10)
    
    total_days_week = models.IntegerField()
    
    average_hours_on_campus = models.FloatField()
    average_hours_on_class = models.FloatField()
    
    median_hours_on_campus = models.FloatField()
    median_hours_on_class = models.FloatField()

    
    total_trips_per_week = models.IntegerField()
    total_classes_per_week = models.IntegerField()

    
    
    
    
