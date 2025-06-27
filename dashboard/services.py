from AllokAcads.models import Ambient
from dashboard.models import ProfessorStatistics
from django.db.models import Sum, Avg, Min, Max
from collections import defaultdict
import numpy as np

class calculateProfessor():
    @staticmethod
    def statistics(ambient_id):
        try: 
            ambient = Ambient.objects.get(id = ambient_id)
        
        except Ambient.DoesNotExist:
            print("Error: Timetable doesn't exist")
            return

        if not ambient.published_timetable:
            return
        
        ProfessorStatistics.objects.filter(ambient=ambient).delete()
            
        allocations = ambient.published_timetable.table.prefetch_related('activitie__tprofessor')
        
        professor_schedule = defaultdict(lambda: defaultdict(list))
        
        for allocation in allocations:
            day = allocation.line
            period = allocation.column
            
            for activity in allocation.activitie.all():
                if activity.tprofessor: 
                    professor = activity.tprofessor
                    professor_schedule[professor][day].append(period)
                
        for professor, schedule in professor_schedule.items():
            for day, periods in schedule.items():
                number_of_periods = len(periods) 
                first_period = min(periods)
                last_period = max(periods)
                
                periods_on_campus = (last_period - first_period) + 1
                periods_interval = periods_on_campus - number_of_periods
                
                if periods_on_campus > 0: 
                    day_efficiency = (number_of_periods / periods_on_campus)
                else: 
                    day_efficiency = 0
                    
                ProfessorStatistics.objects.update_or_create(
                    ambient = ambient,
                    professor = professor,
                    semester = 'vazio',
                    day = day, 
                    defaults = {
                    'periods_on_campus': periods_on_campus,
                    'periods_interval': periods_interval,
                    'number_of_periods': number_of_periods,
                    'day_efficiency': day_efficiency,
                    'trips_to_campus': 1
                    }
                )
                
    @staticmethod
    def filter_by_ambient_and_semester(semester, ambient_id = None):
        pass 
    
    @staticmethod                     
    def average_periods_interval(ambient_id = None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        result = data.aggregate(average_periods = Avg('periods_interval'))
        
        return result['average_periods']

    @staticmethod
    def average_trips(ambient_id = None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        result = data.aggregate(trips_to_campus = Avg('trips_to_campus'))
        return result['trips_to_campus']

    @staticmethod
    def average_periods(ambient_id = None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        result = data.aggregate(average_periods = Avg('number_of_periods'))
        return result['average_periods']

    @staticmethod
    def number_professors(ambient_id = None): 
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        return data.values('professor').distinct().count()

    @staticmethod
    def get_timetable_quality(ambient_id = None):
        return 100

    @staticmethod
    def get_user_ambient_list(user=None):
        if user is not None:
            return list(user.ambients.all())
        return []
        
    
    @staticmethod
    def get_professor_average_periods_list(ambient_id = None):
        if ProfessorStatistics.objects.exists(): 
            data = ProfessorStatistics.objects.all()
            
            if ambient_id:
                data = data.filter(ambient = ambient_id)
            
            result = data.values('professor__user__name').annotate(periods_list = Avg('number_of_periods')).order_by('professor__user__name')
            return list(result)
        else:
            return []
    
    def median_professor_periods(ambient_id = None):
        if ProfessorStatistics.objects.exists(): 
            data = ProfessorStatistics.objects.all()
            
            if ambient_id:
                data = data.filter(ambient = ambient_id)
            
            result = data.values_list('number_of_periods', flat = True)
            np.median(list(result))

