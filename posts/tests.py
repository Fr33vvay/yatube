from django.test import TestCase
from django.urls import reverse

from .models import Post, User


class TestPostCreation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)
        self.post_text = 'New text'

    def test_new_post(self):
        response = self.client.post(reverse('new_post'),
                                    {'text': self.post_text}, follow=True)
        self.assertEqual(response.status_code, 200, msg='Пост не создается')
        self.assertRedirects(response, reverse('index'), status_code=302,
                             target_status_code=200,
                             msg_prefix='Нет редиректа на главную страницу')

        new_post = Post.objects.filter(text=self.post_text)
        self.assertTrue(new_post, msg='Пост не сохранился в БД')
        self.assertEqual(new_post.count(), 1, msg='Больше одного поста')

    def test_noname_cant_create_post(self):
        self.client.logout()
        response = self.client.post(reverse('new_post'),
                                    {'text': self.post_text}, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200,
                             msg_prefix='Неавторизованный пользователь'
                                        'может писать пост')

        new_post = Post.objects.filter(text=self.post_text)
        self.assertFalse(new_post, msg='Неавторизованный пользователь'
                                       'создал пост')


class TestDisplayPost(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)
        self.post_text = 'New text'
        self.edited_post_text = 'Edited text'

    def test_new_post_everywhere(self):
        new_post = Post.objects.create(text=self.post_text, author=self.user)

        resp_index = self.client.get(reverse('index'))
        self.assertContains(resp_index, new_post.text,
                            msg_prefix='Поста нет на главной странице')

        resp_profile = self.client.get(reverse('profile', kwargs={
            'username': self.user.username
        }))
        self.assertContains(resp_profile, new_post.text,
                            msg_prefix='Поста нет на странице пользователя')

        resp_post = self.client.get(reverse('post_view', kwargs={
            'username': self.user.username,
            'post_id': 1
        }))
        self.assertContains(resp_post, new_post.text,
                            msg_prefix='Поста нет на его собственной странице')

    def test_edit_post_everywhere(self):
        new_post = Post.objects.create(text=self.post_text, author=self.user)
        self.client.post((reverse('post_edit', kwargs={
            'username': new_post.author.username,
            'post_id': new_post.pk
        })),
                         {'text': self.edited_post_text}, follow=True)

        resp_index = self.client.get(reverse('index'))
        self.assertContains(resp_index, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'главной странице')

        resp_profile = self.client.get(reverse('profile', kwargs={
            'username': new_post.author.username
        }))
        self.assertContains(resp_profile, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'странице пользователя')

        resp_post = self.client.get(reverse('post_view', kwargs={
            'username': new_post.author.username,
            'post_id': new_post.pk
        }))
        self.assertContains(resp_post, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'его собственной странице')


class TestPostEdit(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)
        self.post_text = 'New text'
        self.edited_post_text = 'Edited text'

    def test_edit_post(self):
        new_post = Post.objects.create(text=self.post_text, author=self.user)
        response = self.client.post((reverse('post_edit', kwargs={
            'username': new_post.author.username,
            'post_id': new_post.pk
        })),
                         {'text': self.edited_post_text}, follow=True)

        self.assertEqual(response.status_code, 200,
                         msg='Пост не редактируется')
        self.assertRedirects(response, reverse('post_view', kwargs={
            'username': new_post.author.username,
            'post_id': new_post.pk}),
                             status_code=302, target_status_code=200,
                             msg_prefix='Нет редиректа на страницу поста')

        refresh_post = Post.objects.filter(text=self.edited_post_text)
        edited_post = Post.objects.filter(text=self.post_text)
        self.assertTrue(refresh_post, msg='Пост не редактируется')
        self.assertEqual(refresh_post.count(), 1, msg='Больше одного поста')
        self.assertFalse(edited_post, msg='Редактируемый пост не изменился')


class TestPathErrors(TestCase):
    def test_404_error(self):
        url = '127.0.0.1:8000/e21n213kno21on21'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404,
                         msg='Не вызывается ошибка 404')