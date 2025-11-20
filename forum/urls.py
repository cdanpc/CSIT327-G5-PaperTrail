from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Page Views
    path('', views.forum_home, name='home'),
    path('topic/<int:topic_id>/', views.topic_threads, name='topic_threads'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    
    # API Endpoints
    path('api/topics/', views.api_get_topics, name='api_get_topics'),
    path('api/topic/<int:topic_id>/threads/', views.api_get_topic_threads, name='api_get_topic_threads'),
    path('api/thread/', views.api_create_thread, name='api_create_thread'),
    path('api/thread/<int:thread_id>/posts/', views.api_get_thread_posts, name='api_get_thread_posts'),
    path('api/thread/<int:thread_id>/post/', views.api_create_post, name='api_create_post'),
]
