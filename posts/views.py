from django.shortcuts import render, get_object_or_404
from .models import Post, Group
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    latest = Post.objects.order_by('-pub_date')[:11]
    return render(request, 'index.html', {'posts': latest})


@login_required
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.order_by("-pub_date")[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts})
