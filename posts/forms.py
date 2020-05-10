from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', )
        help_texts = {
            'text': 'Интернет помнит всё',
            'group': 'Выберите сообщество для публикации. '
                     'Если, конечно, хотите.'
        }
