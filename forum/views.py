from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
import json

from .models import ForumTopic, ForumThread, ForumPost


# ============================================================================
# Page Views
# ============================================================================

@login_required
def forum_home(request):
    """Main forum page showing all topics"""
    return render(request, 'forum/forum_home.html')


@login_required
def topic_threads(request, topic_id):
    """Show all threads for a specific topic"""
    topic = get_object_or_404(ForumTopic, pk=topic_id)
    return render(request, 'forum/topic_threads.html', {'topic': topic})


@login_required
def thread_detail(request, thread_id):
    """Show thread with all posts/replies"""
    thread = get_object_or_404(ForumThread, pk=thread_id)
    return render(request, 'forum/thread_detail.html', {'thread': thread})


# ============================================================================
# API Endpoints (JSON Responses)
# ============================================================================

@login_required
@require_http_methods(["GET"])
def api_get_topics(request):
    """
    API: GET /api/forum/topics/
    Fetch list of all forum topics with thread counts
    """
    topics = ForumTopic.objects.annotate(
        thread_count=Count('threads')
    ).values('id', 'name', 'description', 'thread_count')
    
    return JsonResponse({
        'success': True,
        'topics': list(topics)
    })


@login_required
@require_http_methods(["POST"])
def api_create_thread(request):
    """
    API: POST /api/forum/thread/
    Create a new discussion thread
    """
    try:
        data = json.loads(request.body)
        topic_id = data.get('topic_id')
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not all([topic_id, title, content]):
            return JsonResponse({
                'success': False,
                'error': 'Topic, title, and content are required'
            }, status=400)
        
        topic = get_object_or_404(ForumTopic, pk=topic_id)
        
        thread = ForumThread.objects.create(
            topic=topic,
            starter=request.user,
            title=title,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thread created successfully',
            'thread_id': thread.id,
            'thread': {
                'id': thread.id,
                'title': thread.title,
                'starter': thread.starter.username,
                'created_at': thread.created_at.isoformat(),
                'reply_count': 0
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_get_thread_posts(request, thread_id):
    """
    API: GET /api/forum/thread/<id>/posts/
    Fetch all posts/replies for a specific thread
    """
    thread = get_object_or_404(ForumThread, pk=thread_id)
    
    # Get all posts with author info
    posts = thread.posts.select_related('author', 'parent_post').all()
    
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'content': post.content,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'full_name': f"{post.author.first_name} {post.author.last_name}".strip() or post.author.username
            },
            'parent_post_id': post.parent_post.id if post.parent_post else None,
            'reply_count': post.get_reply_count(),
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat()
        })
    
    return JsonResponse({
        'success': True,
        'thread': {
            'id': thread.id,
            'title': thread.title,
            'content': thread.content,
            'starter': {
                'id': thread.starter.id,
                'username': thread.starter.username,
                'full_name': f"{thread.starter.first_name} {thread.starter.last_name}".strip() or thread.starter.username
            },
            'topic': {
                'id': thread.topic.id,
                'name': thread.topic.name
            },
            'created_at': thread.created_at.isoformat(),
            'last_activity_at': thread.last_activity_at.isoformat()
        },
        'posts': posts_data,
        'total_replies': len(posts_data)
    })


@login_required
@require_http_methods(["POST"])
def api_create_post(request, thread_id):
    """
    API: POST /api/forum/thread/<id>/post/
    Submit a new reply/post to a thread
    """
    try:
        thread = get_object_or_404(ForumThread, pk=thread_id)
        data = json.loads(request.body)
        
        content = data.get('content', '').strip()
        parent_post_id = data.get('parent_post_id')
        
        if not content:
            return JsonResponse({
                'success': False,
                'error': 'Content is required'
            }, status=400)
        
        parent_post = None
        if parent_post_id:
            parent_post = get_object_or_404(ForumPost, pk=parent_post_id, thread=thread)
        
        post = ForumPost.objects.create(
            thread=thread,
            author=request.user,
            content=content,
            parent_post=parent_post
        )
        
        # Update thread's last activity
        thread.update_last_activity()
        
        return JsonResponse({
            'success': True,
            'message': 'Reply posted successfully',
            'post': {
                'id': post.id,
                'content': post.content,
                'author': {
                    'id': post.author.id,
                    'username': post.author.username,
                    'full_name': f"{post.author.first_name} {post.author.last_name}".strip() or post.author.username
                },
                'parent_post_id': post.parent_post.id if post.parent_post else None,
                'reply_count': 0,
                'created_at': post.created_at.isoformat(),
                'updated_at': post.updated_at.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
