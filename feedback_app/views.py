from django.shortcuts import render

def login(request):
    return render(request, 'feedback_app/form.html')