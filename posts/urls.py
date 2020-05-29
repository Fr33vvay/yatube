from django.urls import path

from . import views

urlpatterns = [
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('', views.index, name='index'),
    path('new/', views.new_post, name='new_post'),
    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:post_id>/', views.post_view, name='post_view'),
    path('<username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('404/', views.page_not_found, name='404'),
    path('500/', views.server_error, name='500')
]
