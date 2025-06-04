from django.db import models
from AllokAcads.models import Activitie

class ProfessorStats(models.Model):
    professor_count = models.IntegerField()
    professor_average_classes_per_day = models.FloatField()
    
    def get_professor_count(self):
        self.professor_count = Activitie.objects.filter(tprofessor__is_professor=True).count()
    
    def get_professor_median_classes_per_day(self):
        self.professor_average_classes_per_day
    
    
    
