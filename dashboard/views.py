from django.shortcuts import render

def professor_dashboard_view(request): 
    return render(request, 'dashboard/professor.html')
