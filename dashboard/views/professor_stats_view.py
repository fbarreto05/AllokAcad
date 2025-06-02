from ..models import ProfessorStats
from ..dash_app import * 
from django.shortcuts import render



def renderDashboard(request):
    professor_interval_median = 0
    professor_trip_median = 0
    professor_classes_median = 0
    timetabling_quality = 0
    
    context = {
        'professor_interval_median': professor_interval_median,
        'professor_trip_median': professor_trip_median,  
        'professor_classes_median': professor_classes_median, 
        'timetabling_quality': timetabling_quality
    }
    
    return render(request, 'dashboard/dashboard.html', context )
        