from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        help_texts = {
            'text': 'Введите сообщение',
            'group': 'Выберите сообщество для публикации. '
                     'Если, конечно, хотите.'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {'text': 'Оставьте свой комментарий. При себе.'}
