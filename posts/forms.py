from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'text': 'Введите сообщение',
            'group': 'Выберите сообщество для публикации. '
                     'Если, конечно, хотите.'
        }
