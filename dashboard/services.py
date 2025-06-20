from AllokAcads.models import Ambient
from dashboard.models import ProfessorStatistics
from django.db.models import Sum, Avg, Min, Max

class calculateProfessor():
    def average_periods_interval():
        result = ProfessorStatistics.objects.aggregate(average_periods = Avg('periods_interval'))
        return float(result['average_periods'])

    def average_trips():
        result = ProfessorStatistics.objects.aggregate(trips_to_campus = Avg('trips_to_campus'))
        return float(result['trips_to_campus'])

    def average_periods():
        result = ProfessorStatistics.objects.aggregate(average_periods = Avg('number_of_periods'))
        return float(result['average_periods'])

    def number_professors(): 
        return int(ProfessorStatistics.objects.all().count())

    def get_timetable_quality():
        return 100

    def get_ambient_list():
        return Ambient.objects.all()
    
    def get_professor_average_periods_list():
        result = ProfessorStatistics.objects.values('name').annotate(periods_list = Avg('number_of_periods')).order_by('name')
        return list(result)