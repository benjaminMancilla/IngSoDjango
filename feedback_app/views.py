from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    else:
        return redirect('login')
    
def login_view(request):
    if request.method == 'GET':
        return render(request, 'feedback_app/login.html')
    if request.method == 'POST':
        username = request.POST['userName']
        password = request.POST['userPassword']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            #Start session
            auth_login(request, user)
            return render(request, 'feedback_app/home-page')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'feedback_app/login.html')
        
def logout_view(request):
    auth_logout(request)
    return render('login')

@login_required
def homepage(request):
    return render(request, 'feedback_app/home-page.html')

@login_required
def form(request):
    return render(request, 'feedback_app/form.html')