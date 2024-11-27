from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from feedback_app.models import Student, Teacher, User, TeacherStudentSubject, SubjectResume, Feedback, Subject, Question
from datetime import timedelta, datetime, date
import json
from django.utils.safestring import mark_safe

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

@login_required
def add_week(request, teacherId, subjectId):
    # Asegúrate de que el usuario sea profesor
    if not request.user.is_teacher:
        return redirect('home-page')

    teacher = get_object_or_404(Teacher, user_id=teacherId)
    subject = get_object_or_404(Subject, id=subjectId)

    if request.method == "POST":
        summary = request.POST.get('summary', '').strip()
        last_resume = SubjectResume.objects.filter(teacher=teacher, subject=subject).order_by('-date').first()

        # Calcular la fecha de la nueva semana
        new_date = last_resume.date + timedelta(days=7) if last_resume else date.today()

        # Crear la nueva semana
        SubjectResume.objects.create(
            teacher=teacher,
            subject=subject,
            date=new_date,
            resume=summary if summary else f"Resumen de la semana del {new_date}"
        )

        # Redirigir al foro
        return redirect('foro', teacherId=teacherId, subjectId=subjectId)




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
            resumes = SubjectResume.objects.filter(subject=subject, teacher=teacher).select_related(
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
                    'teacherId': teacher_instance.user.id,
                })
            elif subject.type == Subject.EXACTAS:
                context['exactSubjectList'].append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                    'teacherId': teacher_instance.user.id,
                })
            elif subject.type == Subject.COMPLEMENTARIOS:
                context['complementarySubjectList'].append({
                    'subjectId': subject.id,
                    'subjectName': subject.name,
                    'teacherId': teacher_instance.user.id,
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

    if user.is_teacher:
        context['role'] = 'teacher'
        teacher_instance = user.teacher
        # Data for the grade graph
        graph_data = []
        graph_summary = []
        total_avg = 0
        total_feedbacks = 0
        total_expected_feedbacks = 0

        for subject_info in context['navbar']['subjects_info']:
            subject_name = subject_info['subject'].name
            weekly_averages = [
                {
                    'week': week['week_number'],
                    'avg_grade': week['week_avg_grade'] or 0
                }
                for week in subject_info['weeks']
            ]
            graph_data.append({
                'subject': subject_name,
                'weekly_averages': weekly_averages
            })

        
        # Extra data for the feedbacks
        subjects_feedback = []
        for subject_info in context['navbar']['subjects_info']:
            subject = subject_info['subject']
            students_count = TeacherStudentSubject.objects.filter(subject=subject, teacher=teacher_instance).count()

            last_week_feedback_count = 0
            if subject_info['weeks']:                    
                last_week_feedback_count = sum(
                    len(week['feedbacks']) for week in subject_info['weeks'][-1:]
                )

            subjects_feedback.append({
                'subject': subject,
                'students_count': students_count,
                'last_week_feedback_count': last_week_feedback_count
            })

            # Average grade of the subject
            subject_avg = 0
            if subject_info['weeks']:
                subject_avg = sum(
                    week['week_avg_grade'] for week in subject_info['weeks']
                ) / len(subject_info['weeks'])
                
            total_avg += subject_avg

            # Count Feedbacks and expected feedbacks
            feedback_count = sum(len(week['feedbacks']) for week in subject_info['weeks'])
            expected_feedbacks = len(subject_info['weeks']) * students_count
            total_feedbacks += feedback_count
            total_expected_feedbacks += expected_feedbacks

            # Añadir información a la tabla
            graph_summary.append({
                'subject': subject.name,
                'avg_grade': round(subject_avg, 2),
                'feedback_count': feedback_count,
                'feedback_percentage': round((feedback_count / expected_feedbacks) * 100, 2) if expected_feedbacks else 0
            })

        overall_avg = round(total_avg / max(len(context['navbar']['subjects_info']), 1), 2)


        # Serialize the data to JSON
        context['graph_data'] = mark_safe(json.dumps(graph_data))

        context['subjects_feedback'] = subjects_feedback
        context['graph_summary'] = graph_summary
        context['overall_avg'] = overall_avg

    elif user.is_student:
        context['role'] = 'student'

    else:
        context['role'] = 'unknown'

    # Render the home page
    return render(request, 'feedback_app/home-page.html', context)


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

        return render(request, 'feedback_app/foro.html', context)

    return render(request, 'feedback_app/home-page.html')


@login_required
def form(request, subject=None, classId=None, userId=None):
    if request.method == 'GET':
        teacherId = request.GET.get('teacher')  # Recupera lo que mandé con get
        teacher = Teacher.objects.get(user_id = teacherId) # Obtengo al profesor de esa clase

        # Debería accerder al nombre completo, pero por ahora solo tengo el username
        usernameTeacher = teacher.user.username
        studentId = request.GET.get('student')
        subjectId = request.GET.get('subject')

        context={
            'usernameTeacher' : usernameTeacher, # Probablemente también tenga que mandar la clase y el estudiante en POST
        }
        return render(request, 'feedback_app/form.html', context)
    
    if request.method == 'POST': # lógica de mandar form
        #...
        return render(request, 'feedback_app/form.html', context)
