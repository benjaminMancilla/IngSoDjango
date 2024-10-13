from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from datetime import timedelta
from feedback_app.models import Student, Teacher, User, TeacherStudentSubject, SubjectResume, Feedback


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
            return redirect('login')

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def homepage(request):
    user = request.user
    if user.is_student:
        student_instance = Student.objects.get(user=user)
        #Get all tuples of subjects and teachers
        tss_list = TeacherStudentSubject.objects.filter(student=student_instance)

        #Subjects list, each element has all weekly information of each subject
        subjects_info = []

        #Iterate over each tss (subject or subject/teacher tuple)
        for tss in tss_list:
            #Get subject and teacher
            subject = tss.subject
            teacher = tss.teacher
            
            #Get weekly information
            resumes = SubjectResume.objects.filter(subject=subject).order_by('date')

            #List of weekly information of the subject
            weeks = []
            for resume in resumes:
                #Get week feedbacks, compare date with resume date (7 days)
                feedbacks = Feedback.objects.filter(tss=tss, date__gte=resume.date, date__lte=resume.date + timedelta(days=7))

                weeks.append({
                    'date': resume.date,
                    'resume': resume.resume,
                    'feedbacks': feedbacks,
                })

            subjects_info.append({
                'subject': subject,
                'teacher': teacher,
                'weeks': weeks
            })

        #Context info for frontend
        context = {
            'subjects_info': subjects_info
        }
        return render(request, 'feedback_app/home-page.html', context)
    elif user.is_teacher:
        #For the moment, teacher is not implemented
        return render(request, 'feedback_app/home-page.html')
    return render(request, 'feedback_app/home-page.html')

@login_required
def form(request):
    return render(request, 'feedback_app/form.html')