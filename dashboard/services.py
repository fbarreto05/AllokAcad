from AllokAcads.models import Ambient
from dashboard.models import ProfessorStatistics
from django.db.models import Sum, Avg, Min, Max

class calculateProfessor():
    def average_periods_interval(ambient_id = None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        result = data.aggregate(average_periods = Avg('periods_interval'))
        
        return result['average_periods']

    def average_trips(ambient_id = None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        result = data.aggregate(trips_to_campus = Avg('trips_to_campus'))
        return result['trips_to_campus']

    def average_periods(ambient_id = None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        result = data.aggregate(average_periods = Avg('number_of_periods'))
        return result['average_periods']

    def number_professors(ambient_id = None): 
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        return data.values('professor').count()

    def get_timetable_quality(ambient_id = None):
        return 100

    def get_ambient_list():
        return Ambient.objects.all()
    
    def get_professor_average_periods_list(ambient_id = None):
        if ProfessorStatistics.objects.exists(): 
            data = ProfessorStatistics.objects.all()
            
            if ambient_id:
                data = data.filter(ambient = ambient_id)
            
            result = data.values('professor__user__name').annotate(periods_list = Avg('number_of_periods')).order_by('professor__user__name')
            return list(result)
        else:
            return []