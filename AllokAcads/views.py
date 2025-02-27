from django.shortcuts import render, redirect
import random
from .models import User

# Create your views here.

def login(request):
    return render(request, "AllokAcads/login.html")

def login_validate(request):
    identificator = request.POST.get('id')
    password = request.POST.get('password')
   
    user = User.objects.filter(ID = identificator).filter(password = password)

    if(len(user) > 0):   
        return redirect(f'/AllokAcad/home/{identificator}')
    return redirect('/AllokAcad/login')

def register(request):
    return render(request, "AllokAcads/register.html")

def generate_userid():
    identificator = ""
    for i in range(3):
        digit = chr(random.randint(65, 90))
        identificator += digit
    for i in range(6):
        digit = str(random.randint(0, 9))
        identificator += digit
    return identificator

def register_validate(request):
    name = request.POST.get('name')
    if not(len(name.strip()) > 0) and (len(name.strip()) <= 80):
        return redirect('/AllokAcad/register')
    email = request.POST.get('email')
    if not(len(email.strip()) > 3) and (len(email.strip()) <= 320):
        return redirect('/AllokAcad/register')
    password = request.POST.get('password')
    if not(len(password.strip()) > 5) and (len(password.strip()) <= 20):
        return redirect('/AllokAcad/register')
    birthdate = request.POST.get('birthdate')

    while(True):
        identificator = generate_userid()
        user = User.objects.filter(ID = identificator)
        if(len(user) == 0):
            break

    user = User(ID=identificator, name=name, email=email, password=password, birthdate=birthdate)
    user.save()

    return render(request, "AllokAcads/register.html")

def home(request, id):
    user = User.objects.filter(ID = id)
    username = user[0].name
    
    return render(request, "AllokAcads/home.html", {'username' : username})
