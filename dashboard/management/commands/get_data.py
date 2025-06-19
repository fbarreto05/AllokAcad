from dashboard.models import ProfessorStatistics
from AllokAcads.models import Ambient
from collections import defaultdict

class Command(Command): 
    def handle(self, *args, **opitions): 
        
    
    def calculate_semester_statistics(ambient_id):   
        try: 
            ambient = Ambient.objects.get(ambientid = ambient_id)
        except ambient.DoesNotExist:
            print("Error: Timetable doesn't exist")
            return
        
        allocations = ambient.table.prefetch_related('activitie__tprofessor')
        professor_schedule = defaultdict(lambda: defaultdict(list))
        
        for allocation in allocations:
            day = allocation.line
            period = allocation.column
            
            for activity in allocation.activitie.all():
                if activity.professor: 
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
                    
                stats = {
                    'ambient': ambient,
                    'periods_on_campus': periods_on_campus,
                    'periods_interval': periods_interval,
                    'number_of_periods': number_of_periods,
                    'day_efficiency': day_efficiency,
                    'trips_to_campus': 1
                }
                
                ProfessorStatisticsDay.objects.create(
                    professor = professor,
                    timetable = ambient.published_timetable,
                    day = day, 
                    defaults = stats
                )
                
        
                
        