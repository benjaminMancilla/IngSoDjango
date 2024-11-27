from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('login/', views.login_view, name='login'),
    path('home-page/', views.homepage, name='home-page'),
    path('foro/<int:teacherId>/<int:subjectId>/', views.foro, name='foro'),
    path('foro/<int:teacherId>/<int:subjectId>/<int:week_n>/', views.foro, name='foro'),
    path('form/<int:teacherId>/int:subjectId>/<int:userId>/', views.form, name='form'),
    # path('form/', views.form, name='form'),
    path('logout/', views.logout_view, name='logout'),
    path('add-week/<int:teacherId>/<int:subjectId>/', views.add_week, name='add_week'),
]