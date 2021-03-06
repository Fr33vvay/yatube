from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Post, User


def index(request):
    post_list = Post.objects.all()
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
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        else:
            render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = False
    if user.is_authenticated:
        follow = user.follower.filter(author=author).exists()
    post_list = author.posts.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'author': author,
                                            'page': page,
                                            'paginator': paginator,
                                            'follow': follow,
                                            'user': user})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.posts, id=post_id)
    form = CommentForm()
    comments = post.comments.order_by("created")
    return render(request, 'post.html', {'author': author,
                                         'post': post,
                                         'form': form,
                                         'comments': comments})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.posts, id=post_id)
    if author == request.user:
        form = PostForm(request.POST or None, files=request.FILES or None,
                        instance=post)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('post_view', username, post_id)
        return render(request, 'post_edit.html', {'form': form,
                                                  'post': post})
    else:
        return redirect('post_view', username, post_id)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.posts, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('post_view', username, post_id)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path},
                  status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.all().values('author')
    post_list = Post.objects.filter(author__in=authors)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_exsists = user.follower.filter(author=author).exists()
    if user != author and follow_exsists is False:
        follow = user.follower.create(author=author)
        follow.save()
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    follows = user.follower.filter(author=author)
    follows.delete()
    return redirect('index')
