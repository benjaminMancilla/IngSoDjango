from django.urls import path
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('home-page/', views.homepage, name='home-page'),
    path('form/', views.form, name='form'),
]