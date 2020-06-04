import time

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Group, Post

User = get_user_model()

DUMMY_CACHE = {
    'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
}


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

        all_posts = Post.objects.all()
        self.assertEqual(all_posts.count(), 1, msg='Число постов не равно 1')
        my_post = all_posts.last()
        self.assertEqual(my_post.author, self.user, msg='Не тот автор поста')
        self.assertEqual(my_post.text, self.post_text, msg='Не тот текст')

    def test_noname_cant_create_post(self):
        self.client.logout()
        response = self.client.post(reverse('new_post'),
                                    {'text': self.post_text}, follow=True)
        self.assertRedirects(response, '/auth/login/?next=/new/',
                             status_code=302, target_status_code=200,
                             msg_prefix='Неавторизованный пользователь'
                                        'может писать пост')

        all_posts = Post.objects.all()
        self.assertEqual(all_posts.count(), 0,
                         msg='Неавторизованный пользователь создал пост')


class TestDisplayPost(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)
        self.edited_post_text = 'Edited text'
        self.new_post = Post.objects.create(text='New text', author=self.user)

    def test_new_post_everywhere(self):
        resp_index = self.client.get(reverse('index'))
        self.assertContains(resp_index, self.new_post.text,
                            msg_prefix='Поста нет на главной странице')

        resp_profile = self.client.get(reverse('profile', kwargs={
            'username': self.new_post.author.username
        }))
        self.assertContains(resp_profile, self.new_post.text,
                            msg_prefix='Поста нет на странице пользователя')

        resp_post = self.client.get(reverse('post_view', kwargs={
            'username': self.new_post.author.username,
            'post_id': self.new_post.pk
        }))
        self.assertContains(resp_post, self.new_post.text,
                            msg_prefix='Поста нет на его собственной странице')

    @override_settings(CACHES=DUMMY_CACHE)
    def test_edit_post_everywhere(self):
        self.client.post((reverse('post_edit', kwargs={
            'username': self.new_post.author.username,
            'post_id': self.new_post.pk
        })),
                         {'text': self.edited_post_text}, follow=True)

        resp_index = self.client.get(reverse('index'))
        self.assertContains(resp_index, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'главной странице')

        resp_profile = self.client.get(reverse('profile', kwargs={
            'username': self.new_post.author.username
        }))
        self.assertContains(resp_profile, self.edited_post_text,
                            msg_prefix='Измененного поста нет на '
                                       'странице пользователя')

        resp_post = self.client.get(reverse('post_view', kwargs={
            'username': self.new_post.author.username,
            'post_id': self.new_post.pk
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
                                    {'text': self.edited_post_text},
                                    follow=True)

        self.assertEqual(response.status_code, 200,
                         msg='Пост не редактируется')
        self.assertRedirects(response, reverse('post_view', kwargs={
            'username': new_post.author.username,
            'post_id': new_post.pk}),
                             status_code=302, target_status_code=200,
                             msg_prefix='Нет редиректа на страницу поста')

        post_with_new_text = Post.objects.filter(text=self.edited_post_text)
        post_with_previous_text = Post.objects.filter(text=self.post_text)
        self.assertTrue(post_with_new_text,
                        msg='Пост не сохранился после редактирования')
        self.assertEqual(post_with_new_text.count(), 1,
                         msg='Больше одного поста')
        self.assertFalse(post_with_previous_text,
                         msg='В базе остался пост с данными до редактирования')


class TestPathErrors(TestCase):
    def test_404_error(self):
        url = '127.0.0.1:8000/e21n213kno21on21'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404,
                         msg='Не вызывается ошибка 404')


class TestDisplayImg(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)
        self.post_text = 'New text'

    def test_pages_have_images(self):
        with open('media/posts/test.jpg', 'rb') as img:
            self.client.post(reverse('new_post'),
                             {'text': self.post_text, 'image': img},
                             follow=True)
            tag = '<img class="card-img"'
            response = self.client.get(reverse('post_view', kwargs={
                'username': self.user.username,
                'post_id': 1
            }))
            self.assertContains(response, tag,
                                msg_prefix='Нет картинки '
                                           'на странице поста')

            response = self.client.get(reverse('index'))
            self.assertContains(response, tag,
                                msg_prefix='Нет картинки на '
                                           'главной странице')

            response = self.client.get(reverse('profile', kwargs={
                'username': self.user.username
            }))
            self.assertContains(response, tag,
                                msg_prefix='Нет картинки на '
                                           'странице автора')

    def test_group_page_has_image(self):
        self.group = Group.objects.create(title='testgroup', slug='testgroup')
        with open('media/posts/test.jpg', 'rb') as img:
            self.client.post(reverse('new_post'), {'text': 'new text',
                                                   'group': self.group.pk,
                                                   'image': img})
        tag = '<img class="card-img"'
        response = self.client.get(
            reverse('group_posts', args=[self.group.slug]))
        self.assertContains(response, tag, msg_prefix='Нет картинки на '
                                                      'странице группы')


class TestNotImage(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)

    def test_fake_image(self):
        with open('media/posts/ololo.docx', 'rb') as img:
            response = self.client.post(reverse('new_post'),
                                        {'text': 'New text', 'image': img},
                                        follow=True)
            self.assertIn('image', response.context['form'].errors,
                          msg='PDF загружается')


class TestLagCache(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bum',
                                             password='password')
        self.client.force_login(self.user)

    def test_cache(self):
        self.client.post(reverse('new_post'),
                         {'text': 'Some text'}, follow=True)
        response = self.client.get(reverse('index'))
        self.assertNotContains(response, 'Some text',
                               msg_prefix='Пост появился слишком рано')
        time.sleep(20)
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Some text',
                            msg_prefix='Пост не появился')


class TestFollowersSeeNewPost(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author',
                                               password='password')
        self.post_text = 'For my followers'

        self.user_fol = User.objects.create_user(username='follower',
                                                 password='password')
        self.client.force_login(self.user_fol)
        self.client.post(reverse('profile_follow', kwargs={
            'username': self.author.username}))

        self.user_not_fol = User.objects.create_user(username='just_user',
                                                     password='password')

    def test_followers_see(self):
        self.client.force_login(self.author)
        self.client.post(reverse('new_post'),
                         {'text': self.post_text}, follow=True)

        self.client.force_login(self.user_fol)
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, self.post_text,
                            msg_prefix='Пост не появился у подписчика')

    def test_not_followers_dont_see(self):
        self.client.force_login(self.author)
        self.client.post(reverse('new_post'),
                         {'text': self.post_text}, follow=True)

        self.client.force_login(self.user_not_fol)
        response = self.client.get(reverse('follow_index'))
        self.assertNotContains(response, self.post_text,
                               msg_prefix='Пост появился у '
                                          'неподписанного пользователя')


class TestComments(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username='author',
                                               password='password')
        self.post_text = 'My text'
        self.comment = 'Best comment'
        self.new_post = Post.objects.create(text=self.post_text,
                                            author=self.author)
        self.user = User.objects.create_user(username='bum',
                                             password='password')

    def test_authenticated_user_comments(self):
        self.client.force_login(self.user)
        response = self.client.post((reverse('add_comment', kwargs={
            'username': self.author.username,
            'post_id': self.new_post.pk
        })),
                                    {'text': self.comment},
                                    follow=True)
        self.assertEqual(response.status_code, 200, msg='not 200')

        response = self.client.get(reverse('post_view', kwargs={
            'username': self.author.username,
            'post_id': self.new_post.pk
        }))
        self.assertContains(response, self.comment,
                            msg_prefix='Нет комментария')

    def test_noname_comments(self):
        response = self.client.get((reverse('add_comment', kwargs={
            'username': self.author.username,
            'post_id': self.new_post.pk
        })),
                                   follow=True)
        self.assertRedirects(response,
                             f'/auth/login/?next=/{self.author.username}/'
                             f'{self.new_post.pk}/comment/',
                             status_code=302, target_status_code=200,
                             msg_prefix='Неавторизованный пользователь'
                                        'может комментировать пост')

        comment = self.author.comment
        self.assertEqual(comment.count(), 0, msg='Комментарий есть')
