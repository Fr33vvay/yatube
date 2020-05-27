from django.test import TestCase
from django.urls import reverse

from .models import User


class TestHomeWork04(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum', password='12345')
        self.client.force_login(self.user)
        self.post_text = 'New text'
        self.edited_post_text = 'Edited text'
        self.new_post = self.client.post(reverse('new_post'),
                                         {'text': self.post_text}, follow=True)

    def test_create_profile_after_reg(self):
        response = self.client.get(reverse('profile', kwargs={
            'username': self.user.username
        }))
        self.assertEqual(response.status_code, 200,
                         msg='Профиль пользователя не создается')

    def test_new_post(self):
        response = self.new_post
        self.assertEqual(response.status_code, 200, msg='Пост не создается')
        self.assertRedirects(response, reverse('index'),
                             msg_prefix='Нет редиректа на главную страницу')

    def test_noname_user_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200)

    def test_new_post_everywhere(self):
        resp_index = self.client.get(reverse('index'))
        self.assertContains(resp_index, self.post_text,
                            msg_prefix='Поста нет на главной странице')

        resp_profile = self.client.get(reverse('profile', kwargs={
            'username': self.user.username
        }))
        self.assertContains(resp_profile, self.post_text,
                            msg_prefix='Поста нет на странице пользователя')

        resp_post = self.client.get(reverse('post_view', kwargs={
            'username': self.user.username,
            'post_id': 1
        }))
        self.assertContains(resp_post, self.post_text,
                            msg_prefix='Поста нет на его собственной странице')

    def test_edit_post(self):
        response = self.client.post((reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': 1
        })), {'text': self.edited_post_text}, follow=True)
        self.assertEqual(response.status_code, 200,
                         msg='Пост не редактируется')

    def test_edit_post_everywhere(self):
        self.client.force_login(self.user)
        self.client.post((reverse('post_edit', kwargs={
            'username': self.user.username,
            'post_id': 1
        })), {'text': self.edited_post_text}, follow=True)
        resp_index = self.client.get(reverse('index'))
        self.assertContains(resp_index, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'главной странице')

        resp_profile = self.client.get(reverse('profile', kwargs={
            'username': self.user.username
        }))
        self.assertContains(resp_profile, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'странице пользователя')

        resp_post = self.client.get(reverse('post_view', kwargs={
            'username': self.user.username,
            'post_id': 1
        }))
        self.assertContains(resp_post, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'его собственной странице')
