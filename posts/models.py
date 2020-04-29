from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название', max_length=200,
                             unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание',
                                   max_length=5000, blank=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Содержание', blank=True)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               related_name='author_posts',
                               on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name='Группа',
                              related_name='group_posts', blank=True,
                              null=True,
                              on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.author}: {self.text[:15]}'
