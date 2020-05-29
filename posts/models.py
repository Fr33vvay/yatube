from django.contrib.auth import get_user_model
from django.db import models

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
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, verbose_name='Автор',
                               related_name='posts', on_delete=models.CASCADE)
    group = models.ForeignKey(Group, verbose_name='Сообщество',
                              related_name='posts', blank=True, null=True,
                              on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f'{self.author}: {self.text[:15]}'
