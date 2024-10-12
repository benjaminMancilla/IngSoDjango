from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('login/', auth_views.LoginView.as_view(template_name='feedback_app/login.html'), name='login'),
    path('home-page/', views.homepage, name='home-page'),
    path('form/', views.form, name='form'),
]