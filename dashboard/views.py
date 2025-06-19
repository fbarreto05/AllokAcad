from django.shortcuts import render
from django.db.models import Avg
from AllokAcads.models import Ambient
from . import services

def professor_dashboard_view(request):
    average_class_interval = services.calculate_average_class_interval()
    average_trips = services.calculate_average_trips()
    average_classes = services.calculate_average_classes()
    number_of_professors = services.calculate_number_professors()
    timetable_quality = services.get_timetable_quality()
    ambient_list = services.get_ambient_list()
    context = {
        'average_class_interval': average_class_interval, 
        'average_trips': average_trips,
        'average_classes': average_classes,
        'number_of_professors': number_of_professors,
        'timetable_quality': timetable_quality,
        'ambients' : ambient_list,
    }
    return render(request, 'dashboard/professor.html', context)

def space_dashboard_view(request):
    return render(request, 'dashboard/space.html') 