from AllokAcads.models import Ambient
from dashboard.models import ProfessorDaySubject, ProfessorStatistics, Semester
from django.db.models import Sum, Avg, Min, Max, Count
from collections import defaultdict
import numpy as np

class calculateProfessor():
    @staticmethod
    def statistics_semester(semester_id):
        try:
            semester = Semester.objects.get(id=semester_id)
            ambient = semester.ambient
            timetable = semester.timetable
            
        except Semester.DoesNotExist:
            return
        
        if timetable is None:
            return
        
        ProfessorDaySubject.objects.filter(semester = semester).delete()
        ProfessorStatistics.objects.filter(semester = semester).delete()
        
        allocations = timetable.table.prefetch_related('activitie', 'activitie__tsubject', 'activitie__tprofessor')
        
        allocations_data_professor_day_subject = []
        
        for allocation in allocations:
            for activity in allocation.activitie.all():
                if activity.tprofessor and activity.tsubject:
                    
                    allocation_data_professor = ProfessorDaySubject(
                        ambient=ambient,
                        professor=activity.tprofessor,
                        subject=activity.tsubject,
                        semester=semester,
                        day=allocation.column,
                        period=allocation.line,
                    )
                    allocations_data_professor_day_subject.append(allocation_data_professor)
        
        ProfessorDaySubject.objects.bulk_create(allocations_data_professor_day_subject)

        professor_day_periods = defaultdict(lambda: defaultdict(list))
        
        for allocation in allocations_data_professor_day_subject:
            professor = allocation.professor
            day = allocation.day
            professor_day_periods[professor][day].append(allocation.period)
        
        statistics = []
        
        for professor, days in professor_day_periods.items():
            for day, periods in days.items():
                
                number_of_periods = len(periods) 
                first_period = min(periods)
                last_period = max(periods)
                
                periods_on_campus = (last_period - first_period) + 1
                periods_interval = periods_on_campus - number_of_periods
                
                if periods_on_campus > 0: 
                    day_efficiency = (number_of_periods / periods_on_campus)
                else: 
                    day_efficiency = 0
                    
                statistics.append(
                    ProfessorStatistics(
                        ambient=ambient,
                        professor=professor,
                        semester=semester,
                        day=day, 
                        periods_on_campus=periods_on_campus,
                        periods_interval=periods_interval,
                        number_of_periods=number_of_periods,
                        day_efficiency=day_efficiency
                    )
                )
                
        ProfessorStatistics.objects.bulk_create(statistics)   
        
    
    @staticmethod
    def update_statistics_semester(ambient_id):
        try:
            ambient = Ambient.objects.get(id=ambient_id)
            
        except Ambient.DoesNotExist:
            return None
       
        current_semester, created = Semester.objects.get_or_create(
                ambient=ambient,
                is_active=True,
                defaults={
                    'name': ambient.name,
                    'timetable': ambient.published_timetable
                })
        
        if not created:
            if current_semester.timetable != ambient.published_timetable:
                current_semester.timetable = ambient.published_timetable
                current_semester.save()
        
        calculateProfessor.statistics_semester(current_semester.id)
    
    
    @staticmethod
    def get_total_professor_classes(ambient_id=None):
        data = ProfessorDaySubject.objects.all()
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = (
            data.values('professor__user__name', 'subject__name')
            .annotate(
                total_classes=Count('id'),  
                total_periods=Sum('period') )
            .order_by('professor__user__name', 'subject__name')
        )
        return list(result)


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
    @staticmethod
    def get_professor_day_efficiency_list(ambient_id=None):
        
        data = ProfessorStatistics.objects.all()
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        result = []
        for stat in data.select_related('professor__user'):
            nome = stat.professor.user.name if hasattr(stat.professor, 'user') else str(stat.professor)
            result.append({'professor': nome, 'day_efficiency': stat.day_efficiency})
        return result
    
    @staticmethod
    def get_professor_accumulated_efficiency(ambient_id=None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('professor__user__name').annotate(total_efficiency=Sum('day_efficiency')).order_by('professor__user__name')
    
        
        return list(result)

