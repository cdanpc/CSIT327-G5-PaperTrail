"""Dashboard views for students, professors, and admins"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from zoneinfo import ZoneInfo
from datetime import timedelta
from collections import defaultdict
import calendar as _cal

from ..models import User, StudyReminder
from resources.models import Resource, Bookmark, Tag, Rating, Comment
from flashcards.models import Deck, Card, DeckBookmark
from flashcards import services as flashcard_services
from quizzes.models import QuizAttempt, Quiz, QuizBookmark


@login_required
def student_dashboard(request):
    """Student dashboard - accessible to all authenticated users"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('accounts:admin_dashboard')
    if request.user.is_professor:
        return redirect('accounts:professor_dashboard')
    
    # Get user's recent resources and bookmarks
    recent_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:5]
    recent_bookmarks = Bookmark.objects.filter(user=request.user).select_related('resource').order_by('-created_at')[:5]

    # In-progress quizzes
    in_progress_quiz_attempts = QuizAttempt.objects.filter(
        student=request.user, 
        completed_at__isnull=True
    ).select_related('quiz')[:3]

    # Trending Tags (top 6 by resource count in last 7 days)
    cutoff = timezone.now() - timedelta(days=7)
    trending_tags = Tag.objects.annotate(
        recent_count=Count('resources', filter=Q(resources__created_at__gte=cutoff))
    ).order_by('-recent_count', 'name')[:6]

    # Top Rated Resources
    top_rated_resources = Resource.objects.annotate(
        avg_rating=Avg('ratings__stars'),
        rating_count=Count('ratings')
    ).filter(rating_count__gte=3).order_by('-avg_rating')[:5]

    # Upcoming/Explore Quizzes
    upcoming_quizzes = Quiz.objects.exclude(creator=request.user).order_by('-created_at')[:3]

    # Study Reminders
    study_reminders = StudyReminder.objects.filter(
        user=request.user
    ).order_by('completed', 'due_date')[:8]

    # Philippines timezone for activity feed
    ph_tz = ZoneInfo('Asia/Manila')
    manila_now = timezone.localtime(timezone.now(), ph_tz)
    cutoff_2d = manila_now - timedelta(days=2)

    # Dynamic Activity Feed
    feed_events = []
    
    # Resource uploads
    for r in Resource.objects.filter(uploader=request.user, created_at__gte=cutoff_2d).order_by('-created_at')[:10]:
        feed_events.append({
            'timestamp': r.created_at,
            'type': 'upload',
            'icon': 'file-upload',
            'title': f'Uploaded "{r.title}"',
            'meta': r.created_at.strftime('%b %d')
        })
    
    # Resource ratings
    for rt in Rating.objects.filter(user=request.user, created_at__gte=cutoff_2d).select_related('resource').order_by('-created_at')[:10]:
        feed_events.append({
            'timestamp': rt.created_at,
            'type': 'rating',
            'icon': 'star',
            'title': f'Rated "{rt.resource.title}" {rt.stars}★',
            'meta': rt.created_at.strftime('%b %d')
        })
    
    # Resource comments
    for c in Comment.objects.filter(user=request.user, created_at__gte=cutoff_2d).select_related('resource').order_by('-created_at')[:10]:
        feed_events.append({
            'timestamp': c.created_at,
            'type': 'comment',
            'icon': 'comment',
            'title': f'Commented on "{c.resource.title}"',
            'meta': c.created_at.strftime('%b %d')
        })
    
    # Bookmarks
    for bm in Bookmark.objects.filter(user=request.user, created_at__gte=cutoff_2d).select_related('resource').order_by('-created_at')[:10]:
        feed_events.append({
            'timestamp': bm.created_at,
            'type': 'bookmark',
            'icon': 'bookmark',
            'title': f'Bookmarked "{bm.resource.title}"',
            'meta': bm.created_at.strftime('%b %d')
        })
    
    # Flashcard events
    flashcard_events = flashcard_services.get_flashcard_feed_events(request.user, limit=10)
    flashcard_events = [ev for ev in flashcard_events if ev.get('timestamp') and ev['timestamp'] >= cutoff_2d]
    feed_events.extend(flashcard_events)
    
    # Quiz creations
    for quiz in Quiz.objects.filter(creator=request.user, created_at__gte=cutoff_2d).order_by('-created_at')[:10]:
        feed_events.append({
            'timestamp': quiz.created_at,
            'type': 'quiz_create',
            'icon': 'question-circle',
            'title': f'Created quiz "{quiz.title}"',
            'meta': quiz.created_at.strftime('%b %d')
        })
    
    # Quiz attempts
    for attempt in QuizAttempt.objects.filter(student=request.user, completed_at__isnull=False, completed_at__gte=cutoff_2d).select_related('quiz').order_by('-completed_at')[:10]:
        score = f"{attempt.score}/{attempt.total_questions}" if hasattr(attempt, 'score') else ''
        feed_events.append({
            'timestamp': attempt.completed_at,
            'type': 'quiz_complete',
            'icon': 'check-circle',
            'title': f'Completed quiz "{attempt.quiz.title}" {score}',
            'meta': attempt.completed_at.strftime('%b %d')
        })
    
    # Sort all events
    feed_events.sort(key=lambda e: e['timestamp'], reverse=True)
    activity_feed = feed_events[:10]

    # Weekly Upload Stats
    today = manila_now.date()
    weekly_labels = []
    weekly_upload_counts = []
    weekly_quiz_created = []
    weekly_quiz_attempted = []
    weekly_cards_created = []
    weekly_cards_reviewed = []
    weekly_bookmarks_added = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        weekly_labels.append(day.strftime('%a'))
        
        # Uploads
        upload_count = Resource.objects.filter(uploader=request.user, created_at__date=day).count()
        weekly_upload_counts.append(upload_count)
        
        # Quizzes
        quiz_created = Quiz.objects.filter(creator=request.user, created_at__date=day).count()
        quiz_attempted = QuizAttempt.objects.filter(
            student=request.user, 
            completed_at__date=day
        ).values('quiz').distinct().count()
        weekly_quiz_created.append(quiz_created)
        weekly_quiz_attempted.append(quiz_attempted)
        
        # Flashcards
        cards_created = Card.objects.filter(
            deck__owner=request.user,
            created_at__date=day
        ).count()
        studied_decks = Deck.objects.filter(
            owner=request.user,
            last_studied_at__date=day
        )
        cards_reviewed = sum(deck.cards.count() for deck in studied_decks)
        weekly_cards_created.append(cards_created)
        weekly_cards_reviewed.append(cards_reviewed)
        
        # Bookmarks
        bookmarks_added = Bookmark.objects.filter(user=request.user, created_at__date=day).count()
        weekly_bookmarks_added.append(bookmarks_added)
    
    # Calculate maxima for chart scaling
    max_uploads = max(weekly_upload_counts) if weekly_upload_counts else 0
    max_quiz_created = max(weekly_quiz_created) if weekly_quiz_created else 0
    max_quiz_attempted = max(weekly_quiz_attempted) if weekly_quiz_attempted else 0
    max_cards_created = max(weekly_cards_created) if weekly_cards_created else 0
    max_cards_reviewed = max(weekly_cards_reviewed) if weekly_cards_reviewed else 0
    max_bookmarks = max(weekly_bookmarks_added) if weekly_bookmarks_added else 0
    max_overall = max(max_uploads, max_quiz_created, max_quiz_attempted, 
                      max_cards_created, max_cards_reviewed, max_bookmarks)

    weekly_metrics = {
        'labels': weekly_labels,
        'uploads': weekly_upload_counts,
        'quizzes_created': weekly_quiz_created,
        'quizzes_attempted': weekly_quiz_attempted,
        'decks_created': weekly_cards_created,
        'decks_reviewed': weekly_cards_reviewed,
        'bookmarks': weekly_bookmarks_added,
        'max_values': {
            'uploads': max_uploads,
            'quizzes_created': max_quiz_created,
            'quizzes_attempted': max_quiz_attempted,
            'decks_created': max_cards_created,
            'decks_reviewed': max_cards_reviewed,
            'bookmarks': max_bookmarks,
            'overall': max_overall,
        },
        'palette': {
            'uploads': '#0d6efd',
            'quizzes_created': '#ffc107',
            'quizzes_attempted': '#fd7e14',
            'decks_created': '#0dcaf0',
            'decks_reviewed': '#20c997',
            'bookmarks': '#198754'
        }
    }

    # Flashcards summary
    flashcard_summary = flashcard_services.get_flashcard_summary(request.user)
    
    # New Uploads (last 2 days)
    new_uploads_raw = []
    
    # User's recent resources
    for r in Resource.objects.filter(uploader=request.user, created_at__gte=cutoff_2d).order_by('-created_at'):
        new_uploads_raw.append({
            'type': 'resource',
            'title': r.title,
            'created_at': r.created_at,
            'url': reverse('resources:resource_detail', args=[r.pk]),
        })

    # User's recent quizzes
    for q in Quiz.objects.filter(creator=request.user, created_at__gte=cutoff_2d).order_by('-created_at'):
        new_uploads_raw.append({
            'type': 'quiz',
            'title': q.title,
            'created_at': q.created_at,
            'url': reverse('quizzes:quiz_detail', args=[q.pk]),
        })

    # User's recent decks
    for d in Deck.objects.filter(owner=request.user, created_at__gte=cutoff_2d).order_by('-created_at'):
        new_uploads_raw.append({
            'type': 'flashcard',
            'title': d.title,
            'created_at': d.created_at,
            'url': reverse('flashcards:deck_detail', args=[d.pk]),
        })

    # Others' verified/public resources
    for r in Resource.objects.filter(approved=True, is_public=True, created_at__gte=cutoff_2d).exclude(uploader=request.user).order_by('-created_at'):
        new_uploads_raw.append({
            'type': 'resource',
            'title': r.title,
            'created_at': r.created_at,
            'url': reverse('resources:resource_detail', args=[r.pk]),
        })

    # Others' verified/public quizzes
    for q in Quiz.objects.filter(verification_status='verified', is_public=True, created_at__gte=cutoff_2d).exclude(creator=request.user).order_by('-created_at'):
        new_uploads_raw.append({
            'type': 'quiz',
            'title': q.title,
            'created_at': q.created_at,
            'url': reverse('quizzes:quiz_detail', args=[q.pk]),
        })

    # Others' verified/public decks
    for d in Deck.objects.filter(verification_status='verified', visibility='public', created_at__gte=cutoff_2d).exclude(owner=request.user).order_by('-created_at'):
        new_uploads_raw.append({
            'type': 'flashcard',
            'title': d.title,
            'created_at': d.created_at,
            'url': reverse('flashcards:deck_detail', args=[d.pk]),
        })

    new_uploads_raw.sort(key=lambda it: it['created_at'], reverse=True)
    new_uploads = new_uploads_raw[:6]

    # Calendar events
    events_by_day = defaultdict(list)
    current_month = today.month
    current_year = today.year
    
    # Study reminders
    for r in StudyReminder.objects.filter(user=request.user, due_date__month=current_month, due_date__year=current_year):
        if r.due_date:
            events_by_day[r.due_date.day].append({'title': r.title, 'type': 'reminder'})
    
    # Quizzes
    for q in Quiz.objects.filter(created_at__month=current_month, created_at__year=current_year).exclude(creator=request.user):
        events_by_day[q.created_at.day].append({'title': q.title, 'type': 'quiz_explore'})
    for q in Quiz.objects.filter(creator=request.user, created_at__month=current_month, created_at__year=current_year):
        events_by_day[q.created_at.day].append({'title': f'My Quiz: {q.title}', 'type': 'quiz_created'})
    
    # Resources
    for res in Resource.objects.filter(uploader=request.user, created_at__month=current_month, created_at__year=current_year):
        events_by_day[res.created_at.day].append({'title': f'Uploaded: {res.title}', 'type': 'resource_upload'})
    
    # Flashcards
    flashcard_calendar = flashcard_services.get_flashcard_calendar_events(request.user, current_month, current_year)
    for day, fl_events in flashcard_calendar.items():
        events_by_day[day].extend(fl_events)
    
    # Bookmarks
    for bm in Bookmark.objects.filter(user=request.user, created_at__month=current_month, created_at__year=current_year).select_related('resource'):
        events_by_day[bm.created_at.day].append({'title': f'Bookmarked: {bm.resource.title}', 'type': 'bookmark_created'})
    
    # Verified resources
    for res in Resource.objects.filter(verified_at__isnull=False, verified_at__month=current_month, verified_at__year=current_year, uploader=request.user):
        events_by_day[res.verified_at.day].append({'title': f'Verified: {res.title}', 'type': 'resource_verified'})
    
    calendar_events = dict(events_by_day)

    # Build calendar cells
    first_weekday, days_in_month = _cal.monthrange(current_year, current_month)
    sunday_based_offset = (first_weekday + 1) % 7
    calendar_cells = []
    for _ in range(sunday_based_offset):
        calendar_cells.append({'blank': True})
    for day_num in range(1, days_in_month + 1):
        calendar_cells.append({
            'day': day_num,
            'events': calendar_events.get(day_num, []),
            'is_today': day_num == today.day,
        })
    
    # Profile completion
    profile_completion = request.user.get_profile_completion_percentage()
    profile_complete = request.user.check_profile_completion()
    
    # Stats
    total_resources = Resource.objects.filter(uploader=request.user).count()
    
    # Total bookmarks: Count ALL types (resources + quizzes + flashcards) to match bookmark page
    resource_bookmarks = Bookmark.objects.filter(user=request.user).count()
    quiz_bookmarks = QuizBookmark.objects.filter(user=request.user).count()
    deck_bookmarks = DeckBookmark.objects.filter(user=request.user).count()
    total_bookmarks = resource_bookmarks + quiz_bookmarks + deck_bookmarks
    
    quizzes_completed = QuizAttempt.objects.filter(student=request.user, completed_at__isnull=False).count()
    total_quizzes_posted = Quiz.objects.filter(creator=request.user).count()
    
    context = {
        'user': request.user,
        'recent_resources': recent_resources,
        'recent_bookmarks': recent_bookmarks,
        'profile_completion': profile_completion,
        'profile_complete': profile_complete,
        'total_resources': total_resources,
        'total_bookmarks': total_bookmarks,
        'quizzes_completed': quizzes_completed,
        'total_quizzes_posted': total_quizzes_posted,
        'in_progress_quiz_attempts': in_progress_quiz_attempts,
        'trending_tags': trending_tags,
        'top_rated_resources': top_rated_resources,
        'upcoming_quizzes': upcoming_quizzes,
        'study_reminders': study_reminders,
        'activity_feed': activity_feed,
        'weekly_upload_labels': weekly_labels,
        'weekly_upload_counts': weekly_upload_counts,
        'weekly_metrics': weekly_metrics,
        'new_uploads': new_uploads,
        'calendar_events': calendar_events,
        'calendar_cells': calendar_cells,
        'current_month_label': manila_now.strftime('%B %Y'),
        'dashboard_date_str': manila_now.strftime('%B %d'),
        'today': today,
        'total_flashcard_decks': flashcard_summary['total_decks'],
        'total_flashcard_cards': flashcard_summary['total_cards'],
        'recent_decks': flashcard_summary['recent_decks'],
        'last_studied_deck': flashcard_summary['last_studied_deck'],
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def professor_dashboard(request):
    """Professor dashboard - only for professors and admins"""
    if not request.user.is_professor and not request.user.is_staff:
        messages.error(request, 'Access denied. Professor privileges required.')
        return redirect(request.user.get_dashboard_url())

    # Pending verifications
    pending_verifications = Resource.objects.filter(
        verification_status='pending'
    ).order_by('-created_at')[:10]

    pending_quizzes = Quiz.objects.filter(
        verification_status='pending'
    ).order_by('-created_at')[:10]

    pending_decks = Deck.objects.filter(
        verification_status='pending', 
        visibility='public'
    ).order_by('-created_at')[:10]

    # Professor's resources
    professor_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:5]

    # Total platform resources
    total_platform_resources = Resource.objects.count()

    # Total pending
    total_pending = pending_verifications.count() + pending_quizzes.count() + pending_decks.count()

    # Recently verified
    recently_verified_resources = Resource.objects.filter(
        verification_by=request.user,
        verification_status='verified'
    )
    recently_verified_quizzes = Quiz.objects.filter(
        verification_by=request.user,
        verification_status='verified'
    )
    recently_verified_decks = Deck.objects.filter(
        verification_by=request.user,
        verification_status='verified'
    )
    
    total_recently_verified = (recently_verified_resources.count() + 
                                recently_verified_quizzes.count() + 
                                recently_verified_decks.count())
    
    from itertools import chain
    combined_verified = list(chain(
        recently_verified_resources,
        recently_verified_quizzes,
        recently_verified_decks
    ))
    combined_verified.sort(
        key=lambda obj: getattr(obj, 'verified_at', None) or getattr(obj, 'created_at', None), 
        reverse=True
    )
    recently_verified = combined_verified[:5]

    context = {
        'user': request.user,
        'pending_verifications': pending_verifications,
        'pending_quizzes': pending_quizzes,
        'pending_decks': pending_decks,
        'professor_resources': professor_resources,
        'recently_verified': recently_verified,
        'total_pending': total_pending,
        'total_recently_verified': total_recently_verified,
        'total_platform_resources': total_platform_resources,
    }
    return render(request, 'accounts/professor_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard - only for staff/superusers"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    # Statistics
    total_users = User.objects.filter(is_staff=False, is_superuser=False).count()
    total_students = User.objects.filter(
        is_professor=False, 
        is_staff=False, 
        is_superuser=False
    ).count()
    total_professors = User.objects.filter(
        is_professor=True,
        is_staff=False,
        is_superuser=False
    ).count()
    banned_users = User.objects.filter(is_banned=True).count()
    
    # Pending items
    pending_resources = Resource.objects.filter(approved=False).order_by('-created_at')[:10]
    
    from ..models import PasswordResetRequest
    pending_reset_requests = PasswordResetRequest.objects.filter(
        status='pending'
    ).order_by('-requested_at')[:10]
    
    # All users
    all_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'user': request.user,
        'total_users': total_users,
        'total_students': total_students,
        'total_professors': total_professors,
        'banned_users': banned_users,
        'pending_resources': pending_resources,
        'pending_reset_requests': pending_reset_requests,
        'all_users': all_users,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


__all__ = ['student_dashboard', 'professor_dashboard', 'admin_dashboard']
