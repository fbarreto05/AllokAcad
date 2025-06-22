
from django.shortcuts import render
from .services import calculateProfessor
from .dash_app import app 
import json
from django.http import JsonResponse

def professor_dashboard_view(request): 
    
    average_class_interval = calculateProfessor.average_periods_interval()
    average_trips = calculateProfessor.average_trips()
    average_classes = calculateProfessor.average_periods()
    number_of_professors = calculateProfessor.number_professors()
    timetable_quality = calculateProfessor.get_timetable_quality()
    
    ambient_list = calculateProfessor.get_ambient_list()
    
    context = {
        'average_class_interval': average_class_interval, 
        'average_trips': average_trips,
        'average_classes': average_classes,
        'number_of_professors': number_of_professors,
        'timetable_quality': timetable_quality,
        'ambients' : ambient_list,
    }
    return render(request, 'dashboard/professor.html', context)

def update_dashboard_data(request):
    ambient_id = request.GET.get('ambient', None)
    
    average_class_interval = calculateProfessor.average_periods_interval(ambient_id = ambient_id)
    average_trips = calculateProfessor.average_trips(ambient_id = ambient_id)
    average_classes = calculateProfessor.average_periods(ambient_id = ambient_id)
    number_of_professors = calculateProfessor.number_professors(ambient_id = ambient_id)
    timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = ambient_id)
    
    data = {
        'indicators': {
            'average_class_interval': average_class_interval, 
            'average_trips': average_trips,
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
        }
        
    }
    return JsonResponse(data)

def space_dashboard_view(request):
    return render(request, 'dashboard/space.html') 