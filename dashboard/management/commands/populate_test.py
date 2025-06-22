import random
from django.core.management.base import BaseCommand
from dashboard.models import ProfessorStatistics
from AllokAcads.models import Ambient

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        if ProfessorStatistics.objects.all().exists:
            ProfessorStatistics.objects.all().delete()
        
        ambient = Ambient.objects.get(ambientid = 7)
        semesters = ["2025.1", "2025.2"]
        
        for semester in semesters:
            for i in range(5):
                ProfessorStatistics.objects.create(
                    ambient = ambient
                    semester = semester,
                    day = random.randint(0, 6),
                    periods_on_campus = random.randint(1, 10),
                    periods_interval = random.randint(0, 3),
                    number_of_periods = random.randint(1, 7),
                    classes_time = random.randint(1, 3),
                    trips_to_campus = 1,
                    day_efficiency = random.uniform(0.75, 0.95),     
                )