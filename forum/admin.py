from django.contrib import admin
from .models import ForumTopic, ForumThread, ForumPost


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_thread_count', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'starter', 'get_reply_count', 'last_activity_at', 'created_at']
    list_filter = ['topic', 'created_at']
    search_fields = ['title', 'content', 'starter__username']
    date_hierarchy = 'created_at'


@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['thread', 'author', 'parent_post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'thread__title']
    date_hierarchy = 'created_at'
