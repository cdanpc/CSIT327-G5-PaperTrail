from django.db import models
from django.conf import settings
from django.utils import timezone


class ForumTopic(models.Model):
    """
    Predefined CS/IT discussion categories
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_thread_count(self):
        """Get total number of threads in this topic"""
        return self.threads.count()


class ForumThread(models.Model):
    """
    Main discussion thread/question
    """
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='threads')
    starter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='started_threads')
    title = models.CharField(max_length=300)
    content = models.TextField(help_text='Supports Markdown and code blocks')
    last_activity_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_activity_at']
    
    def __str__(self):
        return self.title
    
    def get_reply_count(self):
        """Get total number of replies/posts"""
        return self.posts.count()
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity_at = timezone.now()
        self.save(update_fields=['last_activity_at'])


class ForumPost(models.Model):
    """
    Replies/Comments on threads (supports nesting)
    """
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    content = models.TextField(help_text='Supports Markdown and code blocks')
    parent_post = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f'Post by {self.author.username} on {self.thread.title}'
    
    def get_reply_count(self):
        """Get number of direct replies to this post"""
        return self.replies.count()
