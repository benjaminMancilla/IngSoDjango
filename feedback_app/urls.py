from django.urls import path
from . import views

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('login/', views.login_view, name='login'),
    path('home-page/', views.homepage, name='home-page'),
    # path('home-page/<str:subject>/<int:classId>/', views.homepage, name='home-page'),
    path('form/', views.form, name='form'),
    path('logout/', views.logout_view, name='logout'),
]