from django.db import models
from AllokAcads.models import Activitie

class ProfessorStats(models.Model):
    professor_count = models.IntegerField()
    professor_average_classes_per_day = models.FloatField()
    
    def get_professor_count(self):
        return Activitie.objects.filter(tprofessor__is_professor=True).count()
    
    
    
