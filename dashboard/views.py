from django.shortcuts import render
from .services import calculateProfessor
from django.http import JsonResponse
from django.shortcuts import redirect
from AllokAcads.models import User
import json

def professor_dashboard_view(request): 
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
        
        if user:   
            user_ambients = calculateProfessor.get_user_ambient_list(user)
            
        else:
            user_ambients = []
        
        for ambient in user_ambients:
            calculateProfessor.statistics(ambient_id=ambient.id)
        
        firt_ambient = user_ambients[0]
        
        if firt_ambient:
            average_class_interval = calculateProfessor.average_periods_interval(ambient_id = firt_ambient.id)
            average_trips = calculateProfessor.average_trips(ambient_id = firt_ambient.id)
            average_classes = calculateProfessor.average_periods(ambient_id = firt_ambient.id)
            number_of_professors = calculateProfessor.number_professors(ambient_id = firt_ambient.id)
            timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = firt_ambient.id)
            
            bar_graph_data = calculateProfessor.get_professor_average_periods_list(ambient_id = firt_ambient.id)
            

        else:
            average_class_interval = None
            average_trips = None
            average_classes = None
            number_of_professors = None
            timetable_quality = None
            firt_ambient = None
        context = {
            'average_class_interval': average_class_interval, 
            'average_trips': average_trips,
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
            'ambients': user_ambients,
            'selected_ambient': firt_ambient,
            'user': user,
            'bar_grraph_data': bar_graph_data,
        }
        return render(request, 'dashboard/professor.html', context)
    else:
        return redirect('/')

def update_dashboard_data(request):
    ambient_id = request.GET.get('ambient', None)
    
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
        
    if user:
        user_ambients = calculateProfessor.get_user_ambient_list(user)
        
    else:
        user_ambients = []
        
    selected_ambient = None
    
    if ambient_id:
        for ambient in user_ambients:
            if str(ambient.id) == str(ambient_id):
                selected_ambient = ambient
                break
    
    calculateProfessor.statistics(ambient_id=selected_ambient.id)
    average_class_interval = calculateProfessor.average_periods_interval(ambient_id = selected_ambient.id)
    average_trips = calculateProfessor.average_trips(ambient_id = selected_ambient.id)
    average_classes = calculateProfessor.average_periods(ambient_id = selected_ambient.id)
    number_of_professors = calculateProfessor.number_professors(ambient_id = selected_ambient.id)
    timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = selected_ambient.id)
    
    bar_graph_data = calculateProfessor.get_professor_average_periods_list(ambient_id = selected_ambient.id)   
    
    
    data = {
        'indicators': {
            'average_class_interval': average_class_interval, 
            'average_trips': average_trips,
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
        },
        'bar_graph_data': bar_graph_data,
    }
    return JsonResponse(data)

def space_dashboard_view(request):
    if request.user.is_authenticated:
        user = User.objects.filter(userid = request.user.username)
        return render(request, 'dashboard/space.html', {'user' : user[0]}) 
    else:
        return redirect('/')