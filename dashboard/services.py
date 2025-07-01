from AllokAcads.models import Ambient
from dashboard.models import ProfessorDaySubject, ProfessorStatistics, Semester, SpaceDaySubject, SpaceStatistics
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
    def get_user_ambient_list(user=None):
        if user is not None:
            return list(user.ambients.all())
        
        return []
      
    @staticmethod  
    def get_semester_list(ambient_id = None):
        if ambient_id:
            return Semester.objects.filter(ambient = ambient_id).order_by('-create_at')
        
        return []
    
    @staticmethod
    def get_classes_by_day(ambient_id = None, semester_id = None):
        data = ProfessorDaySubject.objects.all()
        
        if ambient_id:
            data = data.filter(ambient = ambient_id)
        if semester_id:
            data = data.filter(semester = semester_id)
            
        result = data.values('professor__user__name', 'day').annotate(total_classes=Count('id')).order_by('professor__user__name', 'day')
        
        return list(result)
    
    @staticmethod
    def get_total_professor_classes(ambient_id=None):
        data = ProfessorDaySubject.objects.all()
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('professor__user__name', 'subject__name').annotate(total_classes=Count('id'),  total_periods=Sum('period')).order_by('professor__user__name', 'subject__name')
        
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
        average = result['average_periods']
        
        if average: 
            return round(average, 2)
        
        return None

    @staticmethod
    def number_professors(ambient_id = None): 
        data = ProfessorStatistics.objects.all()
        
        if ambient_id: 
            data = data.filter(ambient = ambient_id)
        
        return data.values('professor').distinct().count()

    @staticmethod
    def get_timetable_quality(ambient_id = None):
        if ambient_id is None:
            return 0
            
        try:
            stats = ProfessorStatistics.objects.filter(ambient_id=ambient_id)
            
            if not stats.exists():
                return 0
            
            avg_efficiency = stats.aggregate(avg=Avg('day_efficiency'))['avg'] or 0
            avg_intervals = stats.aggregate(avg=Avg('periods_interval'))['avg'] or 0
            
           
            efficiency_score = min(avg_efficiency * 100, 100)  
        
            if avg_intervals <= 3:
                interval_score = 100
            elif avg_intervals <= 5:
                interval_score = 75
            elif avg_intervals <= 7:
                interval_score = 50
            else:
                interval_score = 25
            
          
            quality_score = (efficiency_score * 0.7) + (interval_score * 0.3)
            
            return round(quality_score, 1)
            
        except Exception:
            return 100  # Valor padrão em caso de erro

  
    
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
        
        result = data.values(professor=('professor__user__name'),day_efficiency=('day_efficiency'))
        return list(result)
    
    @staticmethod
    def get_professor_accumulated_efficiency(ambient_id=None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('professor__user__name').annotate(total_efficiency=Sum('day_efficiency')).order_by('professor__user__name')
    
        
        return list(result)

    @staticmethod
    def get_average_classes_evolution(ambient_id=None):
        data = ProfessorStatistics.objects.all()
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        data = data.values('semester__name').annotate(avg_classes=Avg('number_of_periods')).order_by('semester__name')
        return list(data)
    
    @staticmethod
    def get_professor_metrics_evolution(ambient_id=None):
        data = ProfessorStatistics.objects.all()

        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        data = data.values('semester__name').annotate(avg_periods_on_campus = Avg('periods_on_campus'),avg_periods_interval = Avg('periods_interval'),avg_number_of_periods = Avg('number_of_periods'),avg_day_efficiency = Avg('day_efficiency')).order_by('semester__name')
        
        return list(data)
    
    @staticmethod
    def get_professor_efficiency_and_classes_list(ambient_id=None):
        data = ProfessorStatistics.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('professor__user__name').annotate(avg_day_efficiency=Avg('day_efficiency'), total_classes=Sum('number_of_periods')).order_by('professor__user__name')
        
        return list(result)
    
    
class calculateSpace():
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
        
        SpaceDaySubject.objects.filter(semester=semester).delete()
        SpaceStatistics.objects.filter(semester=semester).delete()
        
        allocations = timetable.table.prefetch_related('activitie', 'activitie__tsubject', 'activitie__tclassroom', 'activitie__tclass')
        allocations_data_space_day_subject = []
        
        for allocation in allocations:
            for activity in allocation.activitie.all():
                if activity.tclassroom and activity.tsubject and activity.tclass:
                    allocation_data_space = SpaceDaySubject(
                        ambient=ambient,
                        classroom=activity.tclassroom,
                        tclass=activity.tclass,
                        subject=activity.tsubject,
                        semester=semester,
                        day=allocation.column,
                        period=allocation.line,
                        classroom_number_of_students=activity.tclassroom.classroom_capacity,
                        class_number_of_students=activity.tclass.number_of_students,
                    )
                    allocations_data_space_day_subject.append(allocation_data_space)
                    
        SpaceDaySubject.objects.bulk_create(allocations_data_space_day_subject)
        
        space_data = defaultdict(lambda: defaultdict(list))
        
        for allocation in allocations_data_space_day_subject:
            classroom = allocation.classroom
            day = allocation.day
            space_data[classroom][day].append(allocation.period)
            
        statistics = []
        
        for classroom, days in space_data.items():
            total_periods_available = 0
            total_periods_use = 0
            for day, periods in days.items():
                
                number_of_periods = len(periods)
                first_period = min(periods)
                last_period = max(periods)  
                
                periods_available = (last_period - first_period) + 1
                periods_use = number_of_periods
                total_periods_available += periods_available
                total_periods_use += periods_use
            
            if total_periods_available > 0:
                use_time_rate = total_periods_use / total_periods_available
     
            statistics.append(
                SpaceStatistics(
                    ambient=ambient,
                    classroom=classroom,
                    semester=semester,
                    total_periods_available=total_periods_available,
                    total_periods_use=total_periods_use,
                    use_time_rate=use_time_rate,
                )
            ) 
            
        SpaceStatistics.objects.bulk_create(statistics)

    @staticmethod
    def update_statistics_semester(ambient_id):
        try:
            ambient = Ambient.objects.get(id=ambient_id) 
            
        except Ambient.DoesNotExist:
            return None
        
        current_semester = Semester.objects.filter(ambient=ambient, is_active=True).order_by('-create_at').first()
        
        if not current_semester:
            current_semester = Semester.objects.create(
                ambient=ambient,
                name=ambient.name,
                timetable=ambient.published_timetable,
                is_active=True
            )
            
        elif current_semester.timetable != ambient.published_timetable:
            current_semester.timetable = ambient.published_timetable
            current_semester.save()
            
        calculateSpace.statistics_semester(current_semester.id)
    
    @staticmethod
    def get_total_periods_spaces(ambient_id=None):
        if ambient_id:
            total = SpaceStatistics.objects.filter(ambient_id=ambient_id).aggregate(total=Sum('total_periods_available'))
            return total['total'] or 0
        return 0

    @staticmethod
    def get_total_spaces(ambient_id=None):
        if ambient_id:
            return SpaceStatistics.objects.filter(ambient_id=ambient_id).count()
        
        return SpaceStatistics.objects.count()

    @staticmethod
    def get_occupied_spaces(ambient_id=None):
        if ambient_id:
            occupied = SpaceStatistics.objects.filter(ambient_id=ambient_id, total_periods_use__gt = 0).count()
            return occupied
        return 0

    @staticmethod
    def get_occupation_rate(ambient_id=None):      
        if ambient_id:
            total_spaces = calculateSpace.get_total_spaces(ambient_id)
            used_spaces = calculateSpace.get_occupied_spaces(ambient_id)
            
            if total_spaces > 0:
                return round((used_spaces / total_spaces) * 100, 2)
            
        return 0

    @staticmethod
    def get_space_efficiency(ambient_id=None):
        if ambient_id:
            stats = SpaceStatistics.objects.filter(ambient_id=ambient_id, total_periods_use__gt = 0)
            
            if not stats.exists():
                return 0
            
            avg_efficiency = stats.aggregate(avg=Avg('use_time_rate'))['avg']
            
            if avg_efficiency is not None:
                return round(avg_efficiency * 100, 2)
            
        return 0
    
    @staticmethod
    def get_total_space_classes(ambient_id=None):
        data = SpaceDaySubject.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('classroom__name', 'subject__name').annotate(total_classes=Count('id'), total_periods=Sum('period')).order_by('classroom__name', 'subject__name')
        
        return list(result)
    
    @staticmethod
    def get_spaces_classes_by_day(ambient_id=None):
        data = SpaceDaySubject.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('classroom__name', 'day').annotate(total_classes=Count('id')).order_by('classroom__name', 'day')
        
        return list(result)
    
    @staticmethod
    def get_space_efficiency_and_classes_list(ambient_id=None):
        data = SpaceStatistics.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('classroom__name').annotate(avg_use_time_rate=Avg('use_time_rate'),total_classes=Sum('total_periods_use')).order_by('classroom__name')
        
        return list(result)
    
    @staticmethod
    def get_space_metrics_evolution(ambient_id=None):
        data = SpaceStatistics.objects.all()
        
        if ambient_id:
            data = data.filter(ambient=ambient_id)
        
        result = data.values('semester__name').annotate(avg_total_periods_available=Avg('total_periods_available'),avg_total_periods_use=Avg('total_periods_use'),avg_use_time_rate=Avg('use_time_rate')).order_by('semester__name')
        
        return list(result)