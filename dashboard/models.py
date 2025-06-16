from django.db import models
from AllokAcads.models import Activitie

class ProfessorStatisticsDay(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE, null = True)
    professor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE, null = True)
    date = models.DateField(db_index=True)
    
    semester = models.CharField(max_length = 10)
    
    hours_on_campus = models.FloatField(default=0.0)
    classes_hours = models.FloatField(default=0.0)
    trips_to_campus = models.IntegerField(default=0) 
    number_of_classes = models.IntegerField(default=0)
    classes_interval = models.FloatField(default=0.0)
    day_efficiency = models.FloatField(default=0.0)
    
    create_at = models.DateField(auto_now_add=True)
    class Meta:
        unique_together = ('professor', 'ambient', 'date')       

    

    
    
    
    
