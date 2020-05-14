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
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    member = User.objects.get(username=username)
    post_list = Post.objects.filter(author=member).order_by('-pub_date')
    post_count = len(post_list)
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {'member': member,
                                            'post_count': post_count,
                                            'page': page,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    member = User.objects.get(username=username)
    post = member.posts.get(id=post_id)
    post_list = Post.objects.filter(author=member)
    post_count = len(post_list)
    return render(request, "post.html", {'member': member,
                                         'post': post,
                                         'post_count': post_count})


def post_edit(request, username, post_id):
    return render(request, "post_new.html", {})