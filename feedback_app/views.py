from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from feedback_app.models import Student, Teacher, User, TeacherStudentSubject, SubjectResume, Feedback

# Redirects empty path to login page if user is not authenticated
# or to home page if user is authenticated
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    else:
        return redirect('login')

# Authenticated user is redirected to home page
# Unauthenticated user with GET request render login page
# Unauthenticated user with POST request tries to authenticate
# and if successful is redirected to home page
# if not successful is redirected to login page.
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

#Logs out user and redirects to login page
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

#Renders home page with all the information of the student
@login_required
def homepage(request):
    user = request.user
    if user.is_student:
        student_instance = Student.objects.get(user=user)
        #Get all tuples of subjects and teachers
        tss_list = TeacherStudentSubject.objects.filter(student=student_instance).select_related(
            'subject', 'teacher'
        )

        #Subjects list, each element has all weekly information of each subject
        subjects_info = []

        #Iterate over each tss (subject or subject/teacher tuple)
        for tss in tss_list:
            #Get subject and teacher
            subject = tss.subject
            teacher = tss.teacher
            
            #Get weekly information
            resumes = SubjectResume.objects.filter(subject=subject).select_related(
                'teacher', 'subject').order_by('date')

            #List of weekly information of the subject
            weeks = []
            for resume in resumes:
                #Get week number
                #IMPORTANT: for the moment we asume that the feedback deadline
                #is exactly at the end of the week that the resume was uploaded. 
                week_number = resume.date.isocalendar()[1]

                #Get week feedbacks for the corresponding week number
                feedbacks = Feedback.objects.filter(tss=tss, date__week=week_number).select_related(
                    'tss__teacher__user',
                    'tss__student__user').order_by('date')

                #Add resume, feedbacks and week number to the weeks list
                weeks.append({
                    'date': resume.date,
                    'resume': resume.resume,
                    'feedbacks': feedbacks,
                    'week_number': week_number
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
        #Context structure:
        #{
        #    'subjects_info': [
        #        {
        #            'subject': subject_i,
        #            'teacher': teacher_i,
        #            'weeks': [
        #                {
        #                    'date': date_j,
        #                    'resume': resume_j,
        #                    'feedbacks': [
        #                        {
        #                            'date': date_k,
        #                            'grade': grade_k,
        #                            'content': content_k
        #                        }
        #                    ],
        #                    'week_number': week_number_j
        #                }
        #            ]
        #        }
        #    ]
        #}
        return render(request, 'feedback_app/home-page.html', context)
    elif user.is_teacher:
        #For the moment, teacher is not implemented
        return render(request, 'feedback_app/home-page.html')

@login_required
def form(request):
    return render(request, 'feedback_app/form.html')