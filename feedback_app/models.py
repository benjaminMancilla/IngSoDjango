from django.contrib.auth.models import AbstractUser
from django.db import models

''' Clase que extiende de abstract user

Se ocupa para definir un usuario custom que se usa en la aplicacion, agrega caracterizacion entre los tipos de usuarios de la aplicacion.
'''
class User(AbstractUser):

    STUDENT = 1
    TEACHER = 2
    ROLES = (
        (STUDENT, 'student'),
        (TEACHER, 'teacher')
    )

    role = models.PositiveSmallIntegerField(choices=ROLES)
    
    @property
    def is_student(self):
        return self.role == self.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.TEACHER

''' Clase que representa a un estudiante

Se ocupa para representar los datos guardados de un estudiante, esta relacionado con la clase usuario.
'''
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    mask = models.CharField(max_length=100)

''' Clase que representa a un profesor

Se ocupa para representar los datos de un profesor, esta esta relacionada con la clase de usuario.
'''
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


'''Clase que representa a una asignatura

Se ocupa para guardar cada asigatura, estas tienen un curso asignado, un nombre, el curso, el tipo de asignatura y el id.
'''
class Subject(models.Model):
    I = 1
    II = 2
    III = 3
    IV = 4
    SOCIALES = 1
    EXACTAS = 2
    COMPLEMENTARIOS = 3

    LEVELS = (
        (I, 'primero'),
        (II, 'segundo'),
        (III, 'tercero'),
        (IV, 'cuarto')
    )

    TYPES = (
        (SOCIALES, 'Ciencias Sociales'),
        (EXACTAS, 'Ciencias Exactas'),
        (COMPLEMENTARIOS, 'Complementarios')
    )

    name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(choices=LEVELS)
    type = models.PositiveSmallIntegerField(choices=TYPES)

'''Clase que almacena resumenes de distintas asignaturas

Se ocupa principalmente para almacenar los resumenes periodicos de las asignaturas publicados por los profesores.
'''
class SubjectResume(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    resume = models.CharField(max_length=500)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("teacher", "subject", "date"), name='unique_teacher_subject_date'),
        )


''' Tritupla entre profesor, estudiante y asignatura

Esta tritupla sirve para poder hacer checkeos sobre los feedbacks.
'''
class TeacherStudentSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("teacher", "student", "subject"), name='unique_teacher_student_subject'),
        )


''' Clase que representa a un feedback

Se ocupa para poder almacenar la informacion de un feedback, con nota.
'''
class Feedback(models.Model):
    tss = models.ForeignKey(TeacherStudentSubject, on_delete=models.CASCADE)
    date = models.DateField()
    grade = models.PositiveSmallIntegerField()
    content = models.CharField(max_length=300)
    
    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("tss", "date"), name='unique_tss_date'),
        )

''' Clase que representa una pregunta

Se ocupa para poder almacenar las preguntas realizadas por los estudiantes.
'''
class Question(models.Model):
    tss = models.ForeignKey(TeacherStudentSubject, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)
