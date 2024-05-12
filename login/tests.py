from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class TestUserViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

    def test_user_login(self):
        response = self.client.post(reverse('login'), {'username_or_email': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check if login is successful (redirects)

    def test_user_logout(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Check if logout is successful (redirects)

    def test_user_register(self):
        response = self.client.post(reverse('register'), {'username': 'newuser', 'email': 'new@example.com', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Check if registration is successful (redirects)

    def test_user_profile(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)  # Check if profile page loads successfully

    def test_update_profile(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('update_profile'), {'username': 'updateduser', 'email': 'updated@example.com'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Check if profile update is successful

        # Check if the user object has been updated
        updated_user = User.objects.get(username='updateduser')
        self.assertEqual(updated_user.email, 'updated@example.com')