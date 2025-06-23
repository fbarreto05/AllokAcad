from django.db import models

class ProfessorStatistics(models.Model):
    ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    professor = models.ForeignKey('AllokAcads.Member', on_delete = models.CASCADE)
    semester = models.CharField(max_length = 100)
    
    day = models.IntegerField()
    periods_on_campus = models.IntegerField(default = 0)
    periods_interval = models.IntegerField(default = 0) 
    number_of_periods = models.IntegerField(default = 0)
    classes_time = models.IntegerField(default = 0)
    trips_to_campus = models.IntegerField(default = 0)
    day_efficiency = models.FloatField(default = 0.0)
    
    create_at = models.DateField(auto_now_add = True)
    
class SpaceStatistics(models.Model): 
    #ambient = models.ForeignKey('AllokAcads.Ambient', on_delete = models.CASCADE)
    #classroom = models.ForeignKey('AllokAcads.Classroom', on_delete = models.CASCADE)
    semester = models.CharField(max_length = 100)
    
    create_at = models.DateField(auto_now_add = True)
    
        

    

    
    
    
    
