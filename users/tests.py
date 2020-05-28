from django.test import TestCase
from django.urls import reverse

from posts.models import User


class TestRegistration(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)

    def test_reg_user_has_profile(self):
        response = self.client.get(reverse('profile', kwargs={
            'username': self.user.username
        }))
        self.assertEqual(response.status_code, 200,
                         msg='Профиль пользователя не создается')

    def test_noname_has_not_profile(self):
        response = self.client.get(reverse('profile', kwargs={
            'username': 'noname'}))
        self.assertNotEqual(response.status_code, 200,
                            msg='Профиль пользователя уже есть')

    def test_signup(self):
        self.data = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'password1': 'LS38pdkom',
            'password2': 'LS38pdkom'
        }

        response = self.client.get(reverse('profile', kwargs={
            'username': self.data['username']}))
        self.assertNotEqual(response.status_code, 200,
                            msg='Профиль пользователя уже есть')

        self.client.post(reverse('signup'), self.data)

        response = self.client.get(reverse('profile', kwargs={
            'username': self.data['username']}))
        self.assertEqual(response.status_code, 200,
                         msg='Профиль пользователя не создается')
