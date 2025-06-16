from django.shortcuts import render
from django.db.models import Avg
from AllokAcads.models import Ambient
from .models import Semester

def professor_dashboard_view(request):
    selected_ambient_id = request.GET.get('ambient')
    selected_semester_id = request.GET.get('semester')

    ambients = Ambient.objects.all()
    semesters = Semester.objects.none()
    
    context = {
        'ambients': ambients,
        'semesters': semesters,
        'selected_ambient_id': int(selected_ambient_id) if selected_ambient_id else None,
        'selected_semester_id': int(selected_semester_id) if selected_semester_id else None,
        'average_class_interval': "N/D", 'average_trips': "N/D",
        'average_classes': "N/D", 'timetable_quality': "N/D"
    }
    return render(request, 'dashboard/professor.html', context)

def space_dashboard_view(request):
    return render(request, 'dashboard/space.html') 