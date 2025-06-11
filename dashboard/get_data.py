from .models import ProfessorStatisticsDay
from AllokAcads.models import Ambient


class Data():
    @staticmethod
    def calculate_hours_on_campus(last_class, first_class,):
        if last_class < first_class: 
            return 0
        else: 
            return last_class - first_class
    
    @staticmethod   
    def calculate_classes_hours(number_of_classes):
        return number_of_classes
    
    @staticmethod
    def calculate_classes_interval(hours_on_campus, classes_hours):
        if hours_on_campus < classes_hours:
            return 0
        else: 
            return hours_on_campus - classes_hours
    
    def generateStatistics(self, ambient_id):
        ambient = Ambient.objects.get(ambientid = ambient_id)
        professors = ambient.members.filter(is_professor = True)
        allocations = ambient.published_timetable.table.filter(Activitie__tprofessor__in = professors).select_related('Activitie__tprofessor')
        
        professor_classe_day = {}
        
        for allocation in allocations:
            professor = allocation.Activitie.tprofessor
            day = allocation.line
            column = allocation.column
            
            professor_classe_day[professor][day].append(column)

            if professor not in professor_classe_day:
                professor_classe_day[professor] = {}
            
            if day not in professor_classe_day[professor]:
                professor_classe_day[professor][day] = []
            
            professor_classe_day[professor][day].append(column)

        for professor, schedule in professor_classe_day.items():
            for day, column in schedule.items():
                
                number_of_classes = len(column)
                first_class = min(column)
                last_class = max(column)
                
                hours_on_campus = Data.calculate_hours_on_campus(first_class, last_class)
                classes_hours = Data.calculate_classes_hours(number_of_classes)
                classes_interval = Data.calculate_classes_interval(hours_on_campus, classes_hours)
            
            professor_stats = {
                'hours_on_campus': hours_on_campus, 
                'classes_hours': classes_hours,
                'trips_to_campus': None, 
                'number_of_classes': number_of_classes,
                'classes_interval': classes_interval,
                'day_efficiency': None,
            }
            ProfessorStatisticsDay.objects.update_or_create(
                ambient = ambient,
                professor = professor,
                day = None,
                semester = None,
                defaults = professor_stats,
            )  
                
        