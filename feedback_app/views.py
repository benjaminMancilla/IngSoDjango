from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from feedback_app.models import Student, Teacher, User, TeacherStudentSubject, SubjectResume, Feedback, Subject, Question
from datetime import timedelta, datetime

def calculate_deadline(start_date):
    """
    Calcula el plazo (deadline) y verifica si ya está cerrado.
    """
    # Crear un objeto datetime directamente con la fecha y hora
    deadline = datetime(
        year=start_date.year,
        month=start_date.month,
        day=start_date.day,
        hour=23,
        minute=59,
        second=59
    ) + timedelta(days=6)
    
    # Comparar con el datetime actual (sin zonas horarias)
    current_time = datetime.now()
    is_closed = deadline < current_time

    return deadline, is_closed



## Redirects empty path to login page if user is not authenticated
## or to home page if user is authenticated
def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('home-page')
    else:
        # template = loader.get_template('login.html')
        # return HttpResponse(template.render())
        return redirect('login')

## Authenticated user is redirected to home page
## Unauthenticated user with GET request render login page
## Unauthenticated user with POST request tries to authenticate
## and if successful is redirected to home page
## if not successful is redirected to login page.
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

##Logs out user and redirects to login page
@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')

##Returns the context for the navbar
def navbar_context(user):
    context={
        'socialSubjectList':[],
        'exactSubjectList':[],
        'complementarySubjectList':[],
        'subjects_info':[],
    }

    if user.is_student:
        student_instance = user.student

        ##Get all tuples of subjects and teachers
        tss_list = TeacherStudentSubject.objects.filter(student=student_instance).select_related(
            'subject', 'teacher'
        )

        ##Subjects list, each element has all weekly information of each subject
        subjects_info = []
        
        ##Iterate over each tss (subject or subject/teacher tuple)
        for tss in tss_list:
            ##Get subject and teacher
            subject = tss.subject
            teacher = tss.teacher
            
            if subject.type == Subject.SOCIALES:
                context['socialSubjectList'].append({
                    'subjectId': subject.id,
                    'teacherId': teacher.user.id,
                    'subjectName': subject.name,
                })
            elif subject.type == Subject.EXACTAS:
                context['exactSubjectList'].append({
                    'subjectId': subject.id,
                    'teacherId': teacher.user.id,
                    'subjectName': subject.name,
                })
            elif subject.type == Subject.COMPLEMENTARIOS:
                context['complementarySubjectList'].append({
                    'subjectId': subject.id,
                    'teacherId': teacher.user.id,
                    'subjectName': subject.name,
                })
                
            ##Get weekly information
            resumes = SubjectResume.objects.filter(subject=subject).select_related(
                'teacher', 'subject').order_by('date')

            ##List of weekly information of the subject
            weeks = []
            for resume in resumes:
                ##Get week number
                ##IMPORTANT: for the moment we asume that the feedback deadline
                ##is exactly at the end of the week that the resume was uploaded. 
                week_number = resume.date.isocalendar()[1]

                ##Get week feedbacks for the corresponding week number
                feedbacks = Feedback.objects.filter(tss=tss, date__week=week_number).select_related(
                    'tss__teacher__user',
                    'tss__student__user').order_by('date')
                
                #Get Timer for feedback deadline
                deadline, is_closed = calculate_deadline(resume.date)

                ##Add resume, feedbacks and week number to the weeks list
                weeks.append({
                    'date': resume.date,
                    'resume': resume.resume,
                    'feedbacks': feedbacks,
                    'week_number': week_number,
                    'timer': {
                        'deadline': deadline,
                        'is_closed': is_closed,
                    }
                })

            context['subjects_info'].append({
                'subject': subject,
                'teacher': teacher,
                'weeks': weeks
            })

        return context

    elif user.is_teacher:
        teacher_instance = user.teacher

        # Subjects that the teacher teaches
        subjects = Subject.objects.filter(
            teacherstudentsubject__teacher=teacher_instance
        ).distinct()

        # Subject information
        subjects_info = []

        for subject in subjects:
            # Filter the subjects by type
            if subject.type == Subject.SOCIALES:
                context['socialSubjectList'].append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                })
            elif subject.type == Subject.EXACTAS:
                context['exactSubjectList'].append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                })
            elif subject.type == Subject.COMPLEMENTARIOS:
                context['complementarySubjectList'].append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                })

            # Get the resumes of the subject (all weeks)
            resumes = SubjectResume.objects.filter(
                subject=subject,
                teacher=teacher_instance
            ).order_by('date')

            # Create weekly information
            weeks = []

            # Subject average grade
            subject_grades = []

            for resume in resumes:
                # Week number
                week_number = resume.date.isocalendar()[1]

                # Week feedbacks
                feedbacks = Feedback.objects.filter(
                    tss__subject=subject,
                    tss__teacher=teacher_instance,
                    date__week=week_number
                ).select_related(
                    'tss__student__user',
                    'tss__teacher__user'
                ).order_by('date')

                #Obtain the average grade of the week
                grades = feedbacks.values_list('grade', flat=True)
                grades_list = list(grades)

                #Calculate the average grade of the week
                if grades_list:
                    week_avg_grade = sum(grades_list) / len(grades_list)
                else:
                    week_avg_grade = 7.0

                #Add grades to the subject grades list
                subject_grades.extend(grades_list)

                # Get deadline and check if it is closed
                deadline, is_closed = calculate_deadline(resume.date)

                weeks.append({
                    'date': resume.date,
                    'resume': resume.resume,
                    'feedbacks': feedbacks,
                    'week_number': week_number,
                    'week_avg_grade': week_avg_grade,
                    'timer': {
                        'deadline': deadline,
                        'is_closed': is_closed,
                    }
                })

            # Calculate the average grade of the subject
            if subject_grades:
                subject_avg_grade = sum(subject_grades) / len(subject_grades)
            else:
                subject_avg_grade = 7.0

            subjects_info.append({
                'subject': subject,
                'teacher': teacher_instance,
                'weeks': weeks,
                'subject_avg_grade': subject_avg_grade
            })

        context['subjects_info'] = subjects_info

        return context

    else:
        # Context Vacio para el default

        return context

##Renders home page with all the information of the student
@login_required
def homepage(request, subject=None, classId=None):

    user = request.user

    context = {}
    ## Get the context for the navbar depending on the user
    context['navbar'] = navbar_context(user)

    if user.is_student:
        return render(request, 'feedback_app/home-page.html', context)
    
    elif user.is_teacher:
        return render(request, 'feedback_app/home-page.html', context)
    
    else:
        return render(request, 'feedback_app/home-page.html')

@login_required
def foro(request, teacherId, subjectId):
    user = request.user

    context = {
        'identificadores': {
            'teacher': teacherId,
            'subject': subjectId,
        },
        'mensajes_foro': [],
    }
    
    context['navbar'] = navbar_context(user)

    tss_list = TeacherStudentSubject.objects.filter(teacher=teacherId, subject=subjectId)

    for tss in tss_list:
        question_list = Question.objects.filter(tss=tss)
        for question in question_list:
            context['mensajes_foro'].append({
                'name': tss.student.mask,
                'content': question.content,
            })

    if user.is_student:

        context['identificadores']['student'] = user.id
        
        return render(request, 'feedback_app/foro.html', context)
    elif user.is_teacher:
        ##For the moment, teacher is not implemented


        # context={
        #     'subjectList':[],
        #     'subjects_info':[],
        # }


        # teacher_instance = Teacher.objects.get(user=user)

        # context['teacher'] = user.id
        # ##Get all tuples of subjects and teachers
        # tss_list = TeacherStudentSubject.objects.filter(teacher=teacher_instance).select_related(
        #     'subject', 'teacher'
        # )
        # for tss in tss_list:
        #     ##Get subject and teacher
        #     subject = tss.subject
        #     teacher = tss.teacher
            
            # if subject.name in socialSubjects:
            #     context['socialSubjectList'].append({
            #         'subjectId': subject.id,
            #         'subjectName': subject.name,
            #     })
            # elif subject.name in exactSubjects:
            #     context['exactSubjectList'].append({
            #         'subjectId': subject.id,
            #         'subjectName': subject.name,
            #     })
            # elif subject.name in complementarySubjects:
            #     context['complementarySubjectList'].append({
            #         'subjectId': subject.id,
            #         'subjectName': subject.name,
            #     })


        return render(request, 'feedback_app/home-page.html')
    return render(request, 'feedback_app/home-page.html')

@login_required
def form(request, subject=None, classId=None, userId=None):
    return render(request, 'feedback_app/form.html')