from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def login(request):
    return render(request, 'feedback_app/login.html')

@login_required
def homepage(request):
    return render(request, 'feedback_app/home-page.html')

@login_required
def form(request):
    return render(request, 'feedback_app/form.html')