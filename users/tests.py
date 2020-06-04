from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


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


class TestFollow(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author',
                                               password='password')
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)

    def test_no_follow(self):
        follows = self.user.follower.count()
        self.assertEqual(follows, 0, msg='Есть подписки')

    def test_follow(self):
        response = self.client.post(reverse('profile_follow', kwargs={
            'username': self.author.username}))
        self.assertRedirects(response, reverse('follow_index'),
                             status_code=302, target_status_code=200,
                             msg_prefix='Нет редиректа')

        follows = self.user.follower.count()
        self.assertEqual(follows, 1, msg='Нет подписок')

    def test_unfollow(self):
        self.client.post(reverse('profile_follow', kwargs={
            'username': self.author.username}))

        response = self.client.post(reverse('profile_unfollow', kwargs={
            'username': self.author.username}))
        self.assertRedirects(response, reverse('index'),
                             status_code=302, target_status_code=200,
                             msg_prefix='Нет редиректа')

        follows = self.user.follower.count()
        self.assertEqual(follows, 0, msg='Есть подписки')
