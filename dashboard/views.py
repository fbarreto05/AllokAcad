from django.shortcuts import render
from django.db.models import Avg
from AllokAcads.models import Ambient
from .services import calculateProfessor
from .dash_app import app 
import json

def professor_dashboard_view(request):
    ambient_id = request.GET.get('ambient')
    semester_id = request.GET.get('semester')
    
    average_class_interval = calculateProfessor.average_periods_interval()
    average_trips = calculateProfessor.average_trips()
    average_classes = calculateProfessor.average_periods()
    number_of_professors = calculateProfessor.number_professors()
    timetable_quality = calculateProfessor.get_timetable_quality()
    
    ambient_list = calculateProfessor.get_ambient_list()
    
    data_list = calculateProfessor.get_professor_average_periods_list()
    
    data_dash = {
        'data': data_list
    }
    context = {
        'average_class_interval': average_class_interval, 
        'average_trips': average_trips,
        'average_classes': average_classes,
        'number_of_professors': number_of_professors,
        'timetable_quality': timetable_quality,
        'ambients' : ambient_list,
        'dash_name': 'GraficoDeBarras',
        'dash_data_graph_bar': data_dash,
    }
    
    return render(request, 'dashboard/professor.html', context)

def space_dashboard_view(request):
    return render(request, 'dashboard/space.html') 