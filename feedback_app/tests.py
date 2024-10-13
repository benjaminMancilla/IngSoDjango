from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from feedback_app.models import Student
import random

User = get_user_model()

class AuthenticationTests(TestCase):

    #Create user and student instance
    def setUp(self):
        self.username = 'testuser'
        self.password = 'password123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            role=User.STUDENT
        )
        
        self.student = Student.objects.create(
            user=self.user,
            mask=str(random.randint(0, 1000)).zfill(4) # 4 digit mask (example: 0382)
        )
    
    #Test login view
    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feedback_app/login.html')

    #Test login initits valid session
    def test_login(self):
        response = self.client.post(reverse('login'), {
            'userName': self.username,
            'userPassword': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home-page'))

    #Test login with invalid credentials
    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'userName': 'invalid',
            'userPassword': 'invalid',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('register'))#de prueba, deberia ser login, es para entrar a register
    
    #Test logout view
    def test_logout(self):
        #Init session
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(self.client.session.get('_auth_user_id'))#Check session is empty

    # Test protected home page
    def test_access_protected_home_page(self):
        response = self.client.get(reverse('home-page'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('home-page')}")

    # Test protected form page
    def test_access_protected_form_page(self):
        response = self.client.get(reverse('form'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('form')}")

    # Test that an authenticated user can access home page
    def test_access_protected_home_page_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('home-page'))
        self.assertEqual(response.status_code, 200)

    # Test that an authenticated user can access form page
    def test_access_protected_form_page_authenticated(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('form'))
        self.assertEqual(response.status_code, 200)

    #Test that an authenticated user can't access login page
    def test_authenticated_user_access_login(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('home-page'))
