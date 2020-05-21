from django.test import Client, TestCase
from django.urls import reverse

from .models import Post, User


class TestHomeWork05(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum', password='12345')

    def test_create_profile_after_reg(self):
        response = self.client.get('/bum/')
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        response = self.client.post(reverse('new_post'),
                                    {'text': 'New text', 'author': self.user},
                                    follow=True)
        self.assertEqual(response.status_code, 200)

    def test_noname_user_redirect(self):
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200)
