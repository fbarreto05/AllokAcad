from django.shortcuts import render
from .services import calculateProfessor, calculateSpace
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
            calculateProfessor.update_statistics_semester(ambient.id)
        
        if user_ambients:
            first_ambient = user_ambients[0]
        
        else:
            first_ambient = None
        
        if first_ambient:
            ambient_semeters = calculateProfessor.get_semester_list(ambient_id = first_ambient.id)
            average_class_interval = calculateProfessor.average_periods_interval(ambient_id = first_ambient.id)
            average_classes = calculateProfessor.average_periods(ambient_id = first_ambient.id)
            number_of_professors = calculateProfessor.number_professors(ambient_id = first_ambient.id)
            timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = first_ambient.id)
            bar_graph_data = calculateProfessor.get_total_professor_classes(ambient_id = first_ambient.id)
            polar_graph_data = calculateProfessor.get_classes_by_day(ambient_id = first_ambient.id)
            scatter_graph_data = calculateProfessor.get_professor_efficiency_and_classes_list(ambient_id = first_ambient.id)
            line_graph_data = calculateProfessor.get_professor_metrics_evolution(ambient_id = first_ambient.id)
        
        else:
            ambient_semeters = []
            average_class_interval = None
            average_classes = None
            number_of_professors = None
            timetable_quality = None
            first_ambient = None
            bar_graph_data = []
            polar_graph_data = []
            scatter_graph_data = []
            line_graph_data = []
            
            
        context = {
            'average_class_interval': average_class_interval, 
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
            'ambients': user_ambients,
            'semesters': ambient_semeters,
            'selected_ambient': first_ambient,
            'user': user,
            'bar_graph_data': bar_graph_data,
            'polar_graph_data': polar_graph_data, 
            'scatter_graph_data': scatter_graph_data, 
            'line_graph_data': line_graph_data,
        }
        return render(request, 'dashboard/professor.html', context)
    else:
        return redirect('/')

def update_professor_dashboard_data(request):
    ambient_id = request.GET.get('ambient', None)
    semeter_id = request.GET.get('semester', None)
    
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
    else:
        user = None
        
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
    
    calculateProfessor.update_statistics_semester(ambient_id=selected_ambient.id)
    average_class_interval = calculateProfessor.average_periods_interval(ambient_id = selected_ambient.id)
    average_classes = calculateProfessor.average_periods(ambient_id = selected_ambient.id)
    number_of_professors = calculateProfessor.number_professors(ambient_id = selected_ambient.id)
    timetable_quality = calculateProfessor.get_timetable_quality(ambient_id = selected_ambient.id)
    bar_graph_data = calculateProfessor.get_total_professor_classes(ambient_id = selected_ambient.id)
    polar_graph_data = calculateProfessor.get_classes_by_day(ambient_id = selected_ambient.id)
    scatter_graph_data = calculateProfessor.get_professor_efficiency_and_classes_list(ambient_id = selected_ambient.id)
    line_graph_data = calculateProfessor.get_professor_metrics_evolution(ambient_id = selected_ambient.id)
    
    data = {
        'indicators': {
            'average_class_interval': average_class_interval, 
            'average_classes': average_classes,
            'number_of_professors': number_of_professors,
            'timetable_quality': timetable_quality,
        },
        'bar_graph_data': bar_graph_data,
        'polar_graph_data': polar_graph_data,  
        'scatter_graph_data': scatter_graph_data,
        'line_graph_data': line_graph_data,
    }
    return JsonResponse(data)

def space_dashboard_view(request):
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
        
        if user:   
            user_ambients = calculateProfessor.get_user_ambient_list(user)
        
        else:
            user_ambients = []
        
        for ambient in user_ambients:
            calculateSpace.update_statistics_semester(ambient.id)
        
        if user_ambients:
            first_ambient = user_ambients[0]
        
        else:
            first_ambient = None
            
       
        if first_ambient:
            ambient_semeters = calculateProfessor.get_semester_list(ambient_id = first_ambient.id)
            total_spaces = calculateSpace.get_total_periods_spaces(ambient_id = first_ambient.id)
            occupied_spaces = calculateSpace.get_occupied_spaces(ambient_id = first_ambient.id)
            occupation_rate = calculateSpace.get_occupation_rate(ambient_id = first_ambient.id)
            space_efficiency = calculateSpace.get_space_efficiency(ambient_id = first_ambient.id)
            bar_graph_data = calculateSpace.get_total_space_classes(ambient_id = first_ambient.id)
            polar_graph_data = calculateSpace.get_spaces_classes_by_day(ambient_id = first_ambient.id)
            scatter_graph_data = calculateSpace.get_space_efficiency_and_classes_list(ambient_id = first_ambient.id)
            line_graph_data = calculateSpace.get_space_metrics_evolution(ambient_id = first_ambient.id)
            
        else:
            ambient_semeters = []
            total_spaces = None
            occupied_spaces = None
            occupation_rate = None
            space_efficiency = None
            first_ambient = None
            
        context = {
            'total_periods': total_spaces,
            'occupied_spaces': occupied_spaces,     
            'occupation_rate': occupation_rate,
            'space_efficiency': space_efficiency,
            'user': user,
            'ambients': user_ambients,
            'selected_ambient': first_ambient,
            'semesters': ambient_semeters,
            'bar_graph_data': bar_graph_data,
            'polar_graph_data': polar_graph_data,
            'scatter_graph_data': scatter_graph_data,
            'line_graph_data_': line_graph_data,
        }
        return render(request, 'dashboard/space.html', context)
    else:
        return redirect('/')

def update_space_dashboard_data(request):
    ambient_id = request.GET.get('ambient', None)
    
    if request.user.is_authenticated:
        user = User.objects.filter(userid=request.user.username).first()
    else:
        user = None
        
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
            
    calculateSpace.update_statistics_semester(ambient_id = selected_ambient.id)
    total_spaces = calculateSpace.get_total_spaces(ambient_id = selected_ambient.id)
    occupied_spaces = calculateSpace.get_occupied_spaces(ambient_id = selected_ambient.id)
    occupation_rate = calculateSpace.get_occupation_rate(ambient_id = selected_ambient.id)
    space_efficiency = calculateSpace.get_space_efficiency(ambient_id = selected_ambient.id)
    bar_graph_data = calculateSpace.get_total_space_classes(ambient_id = selected_ambient.id)
    polar_graph_data = calculateSpace.get_spaces_classes_by_day(ambient_id = selected_ambient.id)
    scatter_graph_data = calculateSpace.get_space_efficiency_and_classes_list(ambient_id = selected_ambient.id)
    line_graph_data = calculateSpace.get_space_metrics_evolution(ambient_id = selected_ambient.id)

    data = {
        'indicators': { 
            'total_periods': total_spaces,
            'occupied_spaces': occupied_spaces,     
            'occupation_rate': occupation_rate,
            'space_efficiency': space_efficiency,
        },
        'bar_graph_data': bar_graph_data,
        'polar_graph_data': polar_graph_data,
        'scatter_graph_data': scatter_graph_data,
        'line_graph_data': line_graph_data,
    }    
    
  
    return JsonResponse(data)
