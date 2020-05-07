from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
import datetime as dt


@login_required
def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    return render(request, 'index.html', {'posts': latest})


@login_required
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.order_by("-pub_date")[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = dt.datetime.now()
            post.save()
            success_url = reverse_lazy('index')
            return redirect(success_url)
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


