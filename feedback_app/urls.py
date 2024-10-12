from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('login/', views.login_view, name='login'),
    path('home-page/', views.homepage, name='home-page'),
    path('form/', views.form, name='form'),
]