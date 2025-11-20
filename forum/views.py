from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from django.urls import reverse
import json


def api_login_required(view_func):
    """
    Custom decorator for API endpoints that returns JSON error instead of redirecting to login
    """
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required. Please log in.',
                'redirect': '/accounts/login/'
            }, status=401)
        return view_func(request, *args, **kwargs)
    return wrapped_view


from .models import ForumTopic, ForumThread, ForumPost


# ============================================================================
# Page Views
# ============================================================================

@login_required
def forum_home(request):
    """Main forum page showing all topics"""
    context = {
        'page_title': 'Forum',
        'page_subtitle': 'Explore CS/IT topics, share knowledge, and collaborate with peers'
    }
    return render(request, 'forum/forum_home.html', context)


@login_required
def topic_threads(request, topic_id):
    """Show all threads for a specific topic"""
    topic = get_object_or_404(ForumTopic, pk=topic_id)
    context = {
        'topic': topic,
        'page_title': topic.name,
        'page_subtitle': topic.description,
        'back_url': reverse('forum:home')
    }
    return render(request, 'forum/topic_threads.html', context)


@login_required
def thread_detail(request, thread_id):
    """Show thread with all posts/replies"""
    thread = get_object_or_404(ForumThread, pk=thread_id)
    context = {
        'thread': thread,
        'page_title': thread.title,
        'back_url': reverse('forum:topic_threads', args=[thread.topic.id])
    }
    return render(request, 'forum/thread_detail.html', context)


# ============================================================================
# API Endpoints (JSON Responses)
# ============================================================================

@api_login_required
@require_http_methods(["GET"])
def api_get_topics(request):
    """
    API: GET /api/forum/topics/
    Fetch list of all forum topics with thread counts
    """
    try:
        topics = ForumTopic.objects.annotate(
            thread_count=Count('threads')
        ).values('id', 'name', 'description', 'thread_count')
        
        topics_list = list(topics)
        print(f"API: Returning {len(topics_list)} topics")  # Debug log
        
        return JsonResponse({
            'success': True,
            'topics': topics_list,
            'total_topics': len(topics_list)
        })
    except Exception as e:
        print(f"Error in api_get_topics: {e}")  # Debug log
        return JsonResponse({
            'success': False,
            'error': f'Failed to load topics: {str(e)}',
            'topics': []
        }, status=500)


@api_login_required
@require_http_methods(["GET"])
def api_get_topic_threads(request, topic_id):
    """
    API: GET /api/forum/topic/<id>/threads/
    Fetch all threads for a specific topic
    """
    try:
        topic = get_object_or_404(ForumTopic, pk=topic_id)
        
        threads = topic.threads.select_related('starter').annotate(
            reply_count=Count('posts')
        ).order_by('-last_activity_at')
        
        threads_data = []
        for thread in threads:
            try:
                starter_first = getattr(thread.starter, 'first_name', '') or ''
                starter_last = getattr(thread.starter, 'last_name', '') or ''
                starter_username = getattr(thread.starter, 'username', 'Unknown')
                full_name = f"{starter_first} {starter_last}".strip() or starter_username
                
                threads_data.append({
                    'id': thread.id,
                    'title': thread.title or 'Untitled',
                    'content': (thread.content[:200] + '...') if len(thread.content) > 200 else thread.content,
                    'starter': {
                        'id': thread.starter.id,
                        'username': starter_username,
                        'full_name': full_name
                    },
                    'reply_count': thread.reply_count,
                    'created_at': thread.created_at.isoformat(),
                    'last_activity_at': thread.last_activity_at.isoformat()
                })
            except Exception as thread_error:
                print(f"Error serializing thread {thread.id}: {thread_error}")
                continue
        
        print(f"API: Returning {len(threads_data)} threads for topic {topic_id}")  # Debug log
        
        return JsonResponse({
            'success': True,
            'topic': {
                'id': topic.id,
                'name': topic.name,
                'description': topic.description
            },
            'threads': threads_data,
            'total_threads': len(threads_data)
        })
    except Exception as e:
        print(f"Error in api_get_topic_threads: {e}")  # Debug log
        return JsonResponse({
            'success': False,
            'error': f'Failed to load threads: {str(e)}',
            'threads': []
        }, status=500)


@api_login_required
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


@api_login_required
@require_http_methods(["GET"])
def api_get_thread_posts(request, thread_id):
    """
    API: GET /api/forum/thread/<id>/posts/
    Fetch all posts/replies for a specific thread
    """
    try:
        thread = get_object_or_404(ForumThread, pk=thread_id)
        
        # Get all posts with author info
        posts = thread.posts.select_related('author', 'parent_post').all()
        
        posts_data = []
        for post in posts:
            try:
                # Defensive data extraction
                author_first = getattr(post.author, 'first_name', '') or ''
                author_last = getattr(post.author, 'last_name', '') or ''
                author_username = getattr(post.author, 'username', 'Unknown')
                full_name = f"{author_first} {author_last}".strip() or author_username
                
                posts_data.append({
                    'id': post.id,
                    'content': post.content or '',
                    'author': {
                        'id': post.author.id,
                        'username': author_username,
                        'full_name': full_name
                    },
                    'parent_post_id': post.parent_post.id if post.parent_post else None,
                    'reply_count': post.get_reply_count(),
                    'created_at': post.created_at.isoformat(),
                    'updated_at': post.updated_at.isoformat()
                })
            except Exception as post_error:
                # Log but don't fail the entire request
                print(f"Error serializing post {post.id}: {post_error}")
                continue
        
        # Defensive data extraction for thread
        starter_first = getattr(thread.starter, 'first_name', '') or ''
        starter_last = getattr(thread.starter, 'last_name', '') or ''
        starter_username = getattr(thread.starter, 'username', 'Unknown')
        starter_full_name = f"{starter_first} {starter_last}".strip() or starter_username
        
        return JsonResponse({
            'success': True,
            'thread': {
                'id': thread.id,
                'title': thread.title or 'Untitled',
                'content': thread.content or '',
                'starter': {
                    'id': thread.starter.id,
                    'username': starter_username,
                    'full_name': starter_full_name
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
    except Exception as e:
        # Return error response instead of crashing
        return JsonResponse({
            'success': False,
            'error': f'Failed to load posts: {str(e)}',
            'posts': [],
            'total_replies': 0
        }, status=500)


@api_login_required
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
        
        # Defensive data extraction for response
        author_first = getattr(post.author, 'first_name', '') or ''
        author_last = getattr(post.author, 'last_name', '') or ''
        author_username = getattr(post.author, 'username', 'You')
        full_name = f"{author_first} {author_last}".strip() or author_username
        
        return JsonResponse({
            'success': True,
            'message': 'Reply posted successfully',
            'post': {
                'id': post.id,
                'content': post.content or '',
                'author': {
                    'id': post.author.id,
                    'username': author_username,
                    'full_name': full_name
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
