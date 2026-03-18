from django.urls import path
from .views import (
    category_list_create,
    blog_list_create,
    my_blogs,
    blog_detail,
    blog_comments,
    comment_detail,

    user_dashboard_stats,
)       

urlpatterns = [
    path('categories/', category_list_create, name='categories'),

    path('blogs/', blog_list_create, name='blogs'),
    path('blogs/my/', my_blogs, name='my-blogs'),
    path('blogs/<int:pk>/', blog_detail, name='blog-detail'),

    path('blogs/<int:blog_id>/comments/', blog_comments, name='blog-comments'),
    path('comments/<int:pk>/', comment_detail, name='comment-detail'),
    # dashboard stats
    path('dashboard/stats/', user_dashboard_stats, name='user-dashboard-stats'),

]