from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    else:
        return redirect('login')
    
@login_required
def homepage(request):
    return render(request, 'feedback_app/home-page.html')

@login_required
def form(request):
    return render(request, 'feedback_app/form.html')