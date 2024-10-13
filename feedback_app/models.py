from django.contrib.auth.models import AbstractUser
from django.db import models

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

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    mask = models.CharField(max_length=100)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class Subject(models.Model):
    name = models.CharField(max_length=100)

class SubjectResume(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    resume = models.CharField(max_length=500)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("teacher", "subject", "date"), name='unique_teacher_subject_date'),
        )


class TeacherStudentSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("teacher", "student", "subject"), name='unique_teacher_student_subject'),
        )

class Feedback(models.Model):
    tss = models.ForeignKey(TeacherStudentSubject, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    grade = models.PositiveSmallIntegerField()
    content = models.CharField(max_length=300)
    
    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("tss", "date"), name='unique_tss_date'),
        )

class Question(models.Model):
    tss = models.ForeignKey(TeacherStudentSubject, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)
