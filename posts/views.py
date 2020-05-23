from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.order_by("-pub_date").all()
    paginator = Paginator(posts_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    form = PostForm()
    return render(request, 'new_post.html', {'form': form,
                                             'title': 'Добавить запись',
                                             'button': 'Добавить'})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.order_by('-pub_date')
    post_count = len(post_list)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)  # TODO: paginator's style
    return render(request, 'profile.html', {'author': author,
                                            'post_count': post_count,
                                            'page': page,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.posts, id=post_id)
    post_list = author.posts.order_by('-pub_date')
    post_count = len(post_list)
    return render(request, 'post.html', {'author': author,
                                         'post': post,
                                         'post_count': post_count})


def post_edit(request, username, post_id):
    edit = True
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post', username, post_id)
        form = PostForm(instance=post)
        return render(request, 'new_post.html',
                      {'form': form,
                       'edit': edit,
                       'post': post,
                       'username': username,
                       'title': 'Редактировать запись',
                       'button': 'Сохранить'}
                      )
    else:
        return redirect('post', username, post_id)
