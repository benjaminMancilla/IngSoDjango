from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from feedback_app.models import Student, Teacher, User
import random

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    else:
        return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    if request.method == 'GET':
        return render(request, 'feedback_app/login.html')
    if request.method == 'POST':
        username = request.POST['userName']
        password = request.POST['userPassword']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            #Start session
            auth_login(request, user)
            return redirect('home-page')
        else:
            messages.error(request, 'username: ' + username + ' password: ' + password)
            return redirect('register')#de prueba, deberia ser login, es para entrar a register

#de prueba
def register_view(request):
    if request.method == 'GET':
        return render(request, 'feedback_app/register.html')
    
    if request.method == 'POST':
        username = request.POST['userName']
        password = request.POST['userPassword']
        role = request.POST.get('role', 1)#default student

        user = User.objects.create_user(username=username, password=password, role=role)

        if role == User.STUDENT:
            random_mask = random.randint(0, 1000)
            formatted_mask = f"{random_mask:04}"
            Student.objects.create(user=user, mask=formatted_mask)
        elif role == User.TEACHER:
            Teacher.objects.create(user=user)

        user.save()
        auth_login(request, user)
        return redirect('home-page')
    
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def homepage(request):
    return render(request, 'feedback_app/home-page.html')

@login_required
def form(request):
    return render(request, 'feedback_app/form.html')