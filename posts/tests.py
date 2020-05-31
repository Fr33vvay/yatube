from django.test import TestCase
from django.urls import reverse

from .models import Group, Post, User


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
            self.assertContains(response, tag, msg_prefix='Нет картинки '
                                                          'на странице поста')

            response = self.client.get(reverse('index'))
            self.assertContains(response, tag, msg_prefix='Нет картинки на '
                                                          'главной странице')

            response = self.client.get(reverse('profile', kwargs={
                'username': self.user.username
            }))
            self.assertContains(response, tag, msg_prefix='Нет картинки на '
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
        self.client.login(username='bum', password='password')
        self.post_text = 'New text'

    def test_fake_image(self):
        with open('media/posts/ololo.docx', 'rb') as img:
            response = self.client.post(reverse('new_post'), {'text': '',
                                                              'image': img},
                                        follow=True)
            self.assertIn('image', response.context['form'].errors,
                          msg='PDF загружается')
