from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    ProfileUpdateForm,
    CustomPasswordChangeForm
)
from .models import User, UserStats, UserPreferences, UserSession, Notification, PasswordResetToken, PasswordResetRequest
from resources.models import Resource, Bookmark, Tag, Rating, Comment
from flashcards.models import Deck, Card
from flashcards import services as flashcard_services
from quizzes.models import QuizAttempt, Quiz
from django.db.models import Count, Avg, Q, F
from django.db import models
from zoneinfo import ZoneInfo
from datetime import timedelta
from .models import StudyReminder


# Registration View
class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Handle successful registration"""
        user = form.save()
        messages.success(self.request, 'Account created successfully! Please log in.')
        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        return super().dispatch(request, *args, **kwargs)


# Login View
def login_view(request):
    """Custom login view with role-based redirection"""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.user_cache
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_display_name()}!')
                
                # Check if password change is required
                if user.must_change_password:
                    messages.warning(request, 'You must change your password.')
                    return redirect('accounts:password_change')
                
                # Redirect to appropriate dashboard
                return redirect(user.get_dashboard_url())
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


# Logout View
@login_required
def logout_view(request):
    """Logout user and redirect to landing page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')  # Redirect to landing page


# Student Dashboard
@login_required
def student_dashboard(request):
    """Student dashboard - accessible to all authenticated users"""
    if request.user.is_staff or request.user.is_superuser:
        return redirect('accounts:admin_dashboard')
    if request.user.is_professor:
        return redirect('accounts:professor_dashboard')
    
    # Get user's recent resources and bookmarks (for Bookmarks Quick Access panel)
    recent_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:5]
    recent_bookmarks = Bookmark.objects.filter(user=request.user).select_related('resource').order_by('-created_at')[:5]

    # Continue Studying panel assumptions:
    #   - In-progress quizzes: attempts started but not completed
    #   - Flashcards: most recently updated decks (simulates ongoing study)
    in_progress_quiz_attempts = QuizAttempt.objects.filter(student=request.user, completed_at__isnull=True).select_related('quiz')[:3]

    # Trending Tags (top 6 by resource count in last 7 days)
    cutoff = timezone.now() - timedelta(days=7)
    trending_tags = Tag.objects.annotate(
        recent_count=Count('resources', filter=Q(resources__created_at__gte=cutoff))
    ).order_by('-recent_count', 'name')[:6]

    # Top Rated Resources (avg rating, minimum 3 ratings)
    top_rated_resources = Resource.objects.annotate(
        avg_rating=Avg('ratings__stars'),
        rating_count=Count('ratings')
    ).filter(rating_count__gte=3).order_by('-avg_rating')[:5]

    # Upcoming Quizzes panel limitation:
    # Quiz model has no scheduling fields; we show latest quizzes not by the user as 'Explore'
    upcoming_quizzes = Quiz.objects.exclude(creator=request.user).order_by('-created_at')[:3]

    # Study Reminders
    study_reminders = StudyReminder.objects.filter(user=request.user).order_by('completed', 'due_date')[:8]

    # Philippines-local cutoff for 'recent' items (last 2 days)
    ph_tz = ZoneInfo('Asia/Manila')
    manila_now = timezone.localtime(timezone.now(), ph_tz)
    cutoff_2d = manila_now - timedelta(days=2)

    # Dynamic Activity Feed - comprehensive user actions (limit 10 most recent)
    feed_events = []
    
    # Resource uploads
    recent_uploads = Resource.objects.filter(uploader=request.user, created_at__gte=cutoff_2d).order_by('-created_at')[:10]
    for r in recent_uploads:
        feed_events.append({
            'timestamp': r.created_at,
            'type': 'upload',
            'icon': 'file-upload',
            'title': f'Uploaded "{r.title}"',
            'meta': r.created_at.strftime('%b %d')
        })
    
    # Resource ratings
    recent_ratings = Rating.objects.filter(user=request.user, created_at__gte=cutoff_2d).select_related('resource').order_by('-created_at')[:10]
    for rt in recent_ratings:
        feed_events.append({
            'timestamp': rt.created_at,
            'type': 'rating',
            'icon': 'star',
            'title': f'Rated "{rt.resource.title}" {rt.stars}★',
            'meta': rt.created_at.strftime('%b %d')
        })
    
    # Resource comments
    recent_comments = Comment.objects.filter(user=request.user, created_at__gte=cutoff_2d).select_related('resource').order_by('-created_at')[:10]
    for c in recent_comments:
        feed_events.append({
            'timestamp': c.created_at,
            'type': 'comment',
            'icon': 'comment',
            'title': f'Commented on "{c.resource.title}"',
            'meta': c.created_at.strftime('%b %d')
        })
    
    # Bookmarks created
    recent_bookmarks_activity = Bookmark.objects.filter(user=request.user, created_at__gte=cutoff_2d).select_related('resource').order_by('-created_at')[:10]
    for bm in recent_bookmarks_activity:
        feed_events.append({
            'timestamp': bm.created_at,
            'type': 'bookmark',
            'icon': 'bookmark',
            'title': f'Bookmarked "{bm.resource.title}"',
            'meta': bm.created_at.strftime('%b %d')
        })
    
    # Flashcard events (moved to flashcards.services for separation of concerns)
    flashcard_events = flashcard_services.get_flashcard_feed_events(request.user, limit=10)
    # Keep only events within the last 2 days
    flashcard_events = [ev for ev in flashcard_events if ev.get('timestamp') and ev['timestamp'] >= cutoff_2d]
    feed_events.extend(flashcard_events)
    
    # Quiz creations
    recent_quizzes = Quiz.objects.filter(creator=request.user, created_at__gte=cutoff_2d).order_by('-created_at')[:10]
    for quiz in recent_quizzes:
        feed_events.append({
            'timestamp': quiz.created_at,
            'type': 'quiz_create',
            'icon': 'question-circle',
            'title': f'Created quiz "{quiz.title}"',
            'meta': quiz.created_at.strftime('%b %d')
        })
    
    # Quiz attempts completed
    completed_attempts = QuizAttempt.objects.filter(student=request.user, completed_at__isnull=False, completed_at__gte=cutoff_2d).select_related('quiz').order_by('-completed_at')[:10]
    for attempt in completed_attempts:
        score = f"{attempt.score}/{attempt.total_questions}" if hasattr(attempt, 'score') else ''
        feed_events.append({
            'timestamp': attempt.completed_at,
            'type': 'quiz_complete',
            'icon': 'check-circle',
            'title': f'Completed quiz "{attempt.quiz.title}" {score}',
            'meta': attempt.completed_at.strftime('%b %d')
        })
    
    # Sort all events by timestamp and take top 10
    feed_events.sort(key=lambda e: e['timestamp'], reverse=True)
    activity_feed = feed_events[:10]

    # Weekly Upload Stats (last 7 days) - base on Philippines time
    ph_tz = ZoneInfo('Asia/Manila')
    manila_now = timezone.localtime(timezone.now(), ph_tz)
    today = manila_now.date()
    weekly_labels = []
    weekly_upload_counts = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        label = day.strftime('%a')
        count = Resource.objects.filter(uploader=request.user, created_at__date=day).count()
        weekly_labels.append(label)
        weekly_upload_counts.append(count)

    # Action-Oriented Learning Insights: Track Engagement vs Creation
    # New metrics: Quizzes (Attempts vs Created), Decks (Cards Reviewed vs Created), Bookmarks (Added vs Removed)
    date_sequence = []
    weekly_quiz_created = []
    weekly_quiz_attempted = []
    weekly_cards_created = []
    weekly_cards_reviewed = []
    weekly_bookmarks_added = []
    weekly_bookmarks_removed = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        date_sequence.append(day)
        
        # QUIZZES: Separate creation from attempts
        quiz_created = Quiz.objects.filter(creator=request.user, created_at__date=day).count()
        # Count unique quiz attempts completed that day (engagement metric)
        quiz_attempted = QuizAttempt.objects.filter(
            student=request.user, 
            completed_at__date=day
        ).values('quiz').distinct().count()
        weekly_quiz_created.append(quiz_created)
        weekly_quiz_attempted.append(quiz_attempted)
        
        # DECKS: Count cards created vs cards reviewed (via deck study sessions)
        # Cards created: new cards added to user's decks
        cards_created = Card.objects.filter(
            deck__owner=request.user,
            created_at__date=day
        ).count()
        # Cards reviewed: count decks studied that day and sum their card counts
        studied_decks = Deck.objects.filter(
            owner=request.user,
            last_studied_at__date=day
        )
        cards_reviewed = sum(deck.cards.count() for deck in studied_decks)
        weekly_cards_created.append(cards_created)
        weekly_cards_reviewed.append(cards_reviewed)
        
        # BOOKMARKS: Count added (created) vs removed (deleted)
        # Note: Bookmark model only tracks creation; no deletion timestamp exists
        # Workaround: Track bookmarks added that day
        bookmarks_added = Bookmark.objects.filter(user=request.user, created_at__date=day).count()
        # For "removed" metric: We can't track deletions without a SoftDelete model
        # Alternative: Show bookmarks added as engagement metric
        weekly_bookmarks_added.append(bookmarks_added)
        # Set removed to 0 for now (future enhancement: track unbookmarks)
        weekly_bookmarks_removed.append(0)
    
    # Compute per-metric maxima for dynamic y-axis scaling
    max_uploads = max(weekly_upload_counts) if weekly_upload_counts else 0
    max_quiz_created = max(weekly_quiz_created) if weekly_quiz_created else 0
    max_quiz_attempted = max(weekly_quiz_attempted) if weekly_quiz_attempted else 0
    max_cards_created = max(weekly_cards_created) if weekly_cards_created else 0
    max_cards_reviewed = max(weekly_cards_reviewed) if weekly_cards_reviewed else 0
    max_bookmarks = max(weekly_bookmarks_added) if weekly_bookmarks_added else 0
    
    # Overall max for 'all' view
    max_overall = max(max_uploads, max_quiz_created, max_quiz_attempted, 
                      max_cards_created, max_cards_reviewed, max_bookmarks)

    weekly_metrics = {
        'labels': weekly_labels,
        'uploads': weekly_upload_counts,
        # QUIZZES: Dual metrics (created vs attempted)
        'quizzes_created': weekly_quiz_created,
        'quizzes_attempted': weekly_quiz_attempted,
        # DECKS: Dual metrics (cards created vs reviewed)
        'decks_created': weekly_cards_created,
        'decks_reviewed': weekly_cards_reviewed,
        # BOOKMARKS: Activity metric
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
            'quizzes_attempted': '#fd7e14',  # Orange for attempts
            'decks_created': '#0dcaf0',
            'decks_reviewed': '#20c997',  # Teal for reviews
            'bookmarks': '#198754'  # Green for bookmarks
        }
    }

    # Flashcards summary for dashboard widgets
    flashcard_summary = flashcard_services.get_flashcard_summary(request.user)
    total_flashcard_decks = flashcard_summary['total_decks']
    total_flashcard_cards = flashcard_summary['total_cards']
    recent_decks = flashcard_summary['recent_decks']
    last_studied_deck = flashcard_summary['last_studied_deck']

    # New Uploads (last 2 days) - unified list across Resources, Quizzes, Flashcards
    # Priority: include user's own recent uploads (any status/visibility), then fill with verified+public uploads from others
    from django.urls import reverse
    new_uploads_raw = []

    # User's recent resources
    user_recent_resources = Resource.objects.filter(
        uploader=request.user,
        created_at__gte=cutoff_2d
    ).order_by('-created_at')
    for r in user_recent_resources:
        new_uploads_raw.append({
            'type': 'resource',
            'title': r.title,
            'created_at': r.created_at,
            'url': reverse('resources:resource_detail', args=[r.pk]),
        })

    # User's recent quizzes
    user_recent_quizzes = Quiz.objects.filter(
        creator=request.user,
        created_at__gte=cutoff_2d
    ).order_by('-created_at')
    for q in user_recent_quizzes:
        new_uploads_raw.append({
            'type': 'quiz',
            'title': q.title,
            'created_at': q.created_at,
            'url': reverse('quizzes:quiz_detail', args=[q.pk]),
        })

    # User's recent flashcard decks
    user_recent_decks = Deck.objects.filter(
        owner=request.user,
        created_at__gte=cutoff_2d
    ).order_by('-created_at')
    for d in user_recent_decks:
        new_uploads_raw.append({
            'type': 'flashcard',
            'title': d.title,
            'created_at': d.created_at,
            'url': reverse('flashcards:deck_detail', args=[d.pk]),
        })

    # Others' verified/public resources
    other_resources = Resource.objects.filter(
        approved=True,
        is_public=True,
        created_at__gte=cutoff_2d
    ).exclude(uploader=request.user).order_by('-created_at')
    for r in other_resources:
        new_uploads_raw.append({
            'type': 'resource',
            'title': r.title,
            'created_at': r.created_at,
            'url': reverse('resources:resource_detail', args=[r.pk]),
        })

    # Others' verified/public quizzes
    other_quizzes = Quiz.objects.filter(
        verification_status='verified',
        is_public=True,
        created_at__gte=cutoff_2d
    ).exclude(creator=request.user).order_by('-created_at')
    for q in other_quizzes:
        new_uploads_raw.append({
            'type': 'quiz',
            'title': q.title,
            'created_at': q.created_at,
            'url': reverse('quizzes:quiz_detail', args=[q.pk]),
        })

    # Others' verified/public flashcard decks
    other_decks = Deck.objects.filter(
        verification_status='verified',
        visibility='public',
        created_at__gte=cutoff_2d
    ).exclude(owner=request.user).order_by('-created_at')
    for d in other_decks:
        new_uploads_raw.append({
            'type': 'flashcard',
            'title': d.title,
            'created_at': d.created_at,
            'url': reverse('flashcards:deck_detail', args=[d.pk]),
        })

    # Sort combined items by created_at desc and limit to 6
    new_uploads_raw.sort(key=lambda it: it['created_at'], reverse=True)
    new_uploads = new_uploads_raw[:6]

    # Calendar events aggregation (reminders, quiz creations, resource verifications)
    from collections import defaultdict
    events_by_day = defaultdict(list)
    current_month = today.month
    current_year = today.year
    # Study reminders with due_date in current month/year
    reminder_qs = StudyReminder.objects.filter(user=request.user, due_date__month=current_month, due_date__year=current_year)
    for r in reminder_qs:
        if r.due_date:
            events_by_day[r.due_date.day].append({'title': r.title, 'type': 'reminder'})
    # Quizzes created by others this month (explore)
    quiz_qs_other = Quiz.objects.filter(created_at__month=current_month, created_at__year=current_year).exclude(creator=request.user)
    for q in quiz_qs_other:
        events_by_day[q.created_at.day].append({'title': q.title, 'type': 'quiz_explore'})
    # User's own quiz creations
    quiz_qs_user = Quiz.objects.filter(creator=request.user, created_at__month=current_month, created_at__year=current_year)
    for q in quiz_qs_user:
        events_by_day[q.created_at.day].append({'title': f'My Quiz: {q.title}', 'type': 'quiz_created'})
    # User resource uploads this month
    resource_uploads = Resource.objects.filter(uploader=request.user, created_at__month=current_month, created_at__year=current_year)
    for res in resource_uploads:
        events_by_day[res.created_at.day].append({'title': f'Uploaded: {res.title}', 'type': 'resource_upload'})
    
    # Flashcard calendar events via service and merge
    flashcard_calendar = flashcard_services.get_flashcard_calendar_events(request.user, current_month, current_year)
    for day, fl_events in flashcard_calendar.items():
        events_by_day[day].extend(fl_events)
    
    # User bookmarks created this month
    bookmarks_created = Bookmark.objects.filter(user=request.user, created_at__month=current_month, created_at__year=current_year).select_related('resource')
    for bm in bookmarks_created:
        events_by_day[bm.created_at.day].append({'title': f'Bookmarked: {bm.resource.title}', 'type': 'bookmark_created'})
    
    # Resources verified this month
    resource_verified_qs = Resource.objects.filter(verified_at__isnull=False, verified_at__month=current_month, verified_at__year=current_year, uploader=request.user)
    for res in resource_verified_qs:
        events_by_day[res.verified_at.day].append({'title': f'Verified: {res.title}', 'type': 'resource_verified'})
    
    # Convert to regular dict for template JSON serialization
    calendar_events = dict(events_by_day)

    # Build calendar cells for current month (with leading blanks)
    import calendar as _cal
    first_weekday, days_in_month = _cal.monthrange(current_year, current_month)  # Monday=0
    # Adjust first_weekday to Sunday=0 for our display
    # If first_weekday is 0 (Monday) we need 1 blank; mapping: (Mon->1, Tue->2,... Sun->0)
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
    
    # Phase 8: Profile completion integration
    profile_completion = request.user.get_profile_completion_percentage()
    profile_complete = request.user.check_profile_completion()
    
    # Get total counts for stats
    total_resources = Resource.objects.filter(uploader=request.user).count()
    total_bookmarks = Bookmark.objects.filter(user=request.user).count()
    quizzes_completed = QuizAttempt.objects.filter(student=request.user, completed_at__isnull=False).count()
    # Newly added counts (Tasks 1 & 2)
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
        # Panels 3-7 context
        'in_progress_quiz_attempts': in_progress_quiz_attempts,
        'trending_tags': trending_tags,
        'top_rated_resources': top_rated_resources,
        'upcoming_quizzes': upcoming_quizzes,
        'study_reminders': study_reminders,
        'activity_feed': activity_feed,
        'weekly_upload_labels': weekly_labels,
        'weekly_upload_counts': weekly_upload_counts,
        # New consolidated metrics & feeds
        'weekly_metrics': weekly_metrics,
        'new_uploads': new_uploads,
        'calendar_events': calendar_events,
        'calendar_cells': calendar_cells,
    'current_month_label': manila_now.strftime('%B %Y'),
    'dashboard_date_str': manila_now.strftime('%B %d'),
        'today': today,
        # Flashcards context
        'total_flashcard_decks': total_flashcard_decks,
        'total_flashcard_cards': total_flashcard_cards,
        'recent_decks': recent_decks,
        'last_studied_deck': last_studied_deck,
    }
    return render(request, 'accounts/student_dashboard.html', context)


# Study Reminder CRUD (basic synchronous handlers)
@login_required
def add_study_reminder(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        due_date_raw = request.POST.get('due_date', '').strip()
        due_dt = None
        if due_date_raw:
            try:
                # Parse date (YYYY-MM-DD) into datetime midnight
                from datetime import datetime
                due_dt = datetime.strptime(due_date_raw, "%Y-%m-%d")
            except Exception:
                due_dt = None
        
        if title and due_dt:
            StudyReminder.objects.create(user=request.user, title=title, due_date=due_dt)
            messages.success(request, 'Study reminder added successfully!')
        else:
            messages.error(request, 'Please provide a valid title and due date.')
    return redirect('accounts:student_dashboard')


@login_required
def toggle_study_reminder(request, pk):
    reminder = StudyReminder.objects.filter(pk=pk, user=request.user).first()
    if reminder:
        reminder.completed = not reminder.completed
        reminder.save(update_fields=['completed'])
    return redirect('accounts:student_dashboard')


@login_required
def delete_study_reminder(request, pk):
    reminder = StudyReminder.objects.filter(pk=pk, user=request.user).first()
    if reminder:
        reminder.delete()
    return redirect('accounts:student_dashboard')


# Professor Dashboard
@login_required
def professor_dashboard(request):
    """Professor dashboard - only for professors"""
    if not request.user.is_professor:
        messages.error(request, 'Access denied. Professor privileges required.')
        return redirect(request.user.get_dashboard_url())

    # Get resources awaiting verification
    pending_verifications = Resource.objects.filter(
        verification_status='pending'
    ).order_by('-created_at')[:10]

    # Get quizzes awaiting verification
    from quizzes.models import Quiz
    pending_quizzes = Quiz.objects.filter(
        verification_status='pending'
    ).order_by('-created_at')[:10]

    # Get flashcard decks awaiting verification
    from flashcards.models import Deck
    pending_decks = Deck.objects.filter(
        verification_status='pending', visibility='public'
    ).order_by('-created_at')[:10]

    # Get professor's uploaded resources
    professor_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:5]

    # Calculate total pending verifications (resources + quizzes + decks)
    total_pending = pending_verifications.count() + pending_quizzes.count() + pending_decks.count()

    # Get recently verified resources, quizzes, and decks by this professor
    from quizzes.models import Quiz
    from flashcards.models import Deck
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
    
    # Calculate total recently verified count
    total_recently_verified = recently_verified_resources.count() + recently_verified_quizzes.count() + recently_verified_decks.count()
    
    # Combine and order by verified_at descending, limit to 5 most recent
    from itertools import chain
    combined_verified = list(chain(
        recently_verified_resources,
        recently_verified_quizzes,
        recently_verified_decks
    ))
    combined_verified.sort(key=lambda obj: getattr(obj, 'verified_at', None) or getattr(obj, 'created_at', None), reverse=True)
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
    }
    return render(request, 'accounts/professor_dashboard.html', context)


# Admin Dashboard
@login_required
def admin_dashboard(request):
    """Admin dashboard - only for staff/superusers"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    # Get statistics
    # Total users (excluding superusers/staff from count)
    total_users = User.objects.filter(is_staff=False, is_superuser=False).count()
    
    # Students: Self-registered users (not professors, not staff)
    total_students = User.objects.filter(
        is_professor=False, 
        is_staff=False, 
        is_superuser=False
    ).count()
    
    # Professors: Users with professor flag (admin-created accounts)
    total_professors = User.objects.filter(
        is_professor=True,
        is_staff=False,
        is_superuser=False
    ).count()
    
    # Banned users (any role)
    banned_users = User.objects.filter(is_banned=True).count()
    
    # Get pending resources for approval
    pending_resources = Resource.objects.filter(approved=False).order_by('-created_at')[:10]
    
    # Get pending password reset requests
    pending_reset_requests = PasswordResetRequest.objects.filter(status='pending').order_by('-requested_at')[:10]
    
    # Get all users (limited to 10 for dashboard display)
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


@login_required
def promote_to_professor(request):
    """Promote a student to professor role"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    # Check for user_id in GET parameter (from manage_users page)
    user_id = request.GET.get('promote')
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            
            # Check if user is already a professor
            if user.is_professor:
                messages.warning(request, f'{user.get_display_name()} is already a professor.')
            else:
                user.is_professor = True
                user.save()
                messages.success(request, f'{user.get_display_name()} has been promoted to professor!')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
        
        return redirect('accounts:manage_users')
    
    # If no user_id in GET, return list of students who can be promoted (for legacy form if needed)
    students = User.objects.filter(
        is_professor=False,
        is_staff=False,
        is_superuser=False,
        is_banned=False
    ).order_by('first_name', 'last_name')
    
    context = {
        'students': students,
    }
    return render(request, 'accounts/promote_professor.html', context)


@login_required
def demote_professor(request, user_id):
    """Demote a professor to student role"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    try:
        user = User.objects.get(id=user_id)
        
        # Check if user is a professor
        if not user.is_professor:
            messages.warning(request, f'{user.get_display_name()} is not a professor.')
        else:
            user.is_professor = False
            user.save()
            messages.success(request, f'{user.get_display_name()} has been demoted to student!')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    
    # Redirect back to manage users page if referrer is there
    return redirect('accounts:manage_users')


@login_required
def manage_users(request):
    """Manage all users - view, promote, and demote"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    # Get all non-admin users
    all_users = User.objects.filter(is_staff=False, is_superuser=False).order_by('-date_joined')
    
    # Optional: Add search/filter functionality
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')  # 'professor', 'student', 'banned', or empty for all
    
    if search_query:
        all_users = all_users.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(univ_email__icontains=search_query)
        )
    
    if role_filter == 'professor':
        all_users = all_users.filter(is_professor=True, is_banned=False)
    elif role_filter == 'student':
        all_users = all_users.filter(is_professor=False, is_banned=False)
    elif role_filter == 'banned':
        all_users = all_users.filter(is_banned=True)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(all_users, 20)  # Show 20 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'total_users': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'total_professors': User.objects.filter(is_professor=True, is_staff=False, is_superuser=False).count(),
        'total_students': User.objects.filter(is_professor=False, is_staff=False, is_superuser=False).count(),
        'total_banned': User.objects.filter(is_banned=True, is_staff=False, is_superuser=False).count(),
    }
    return render(request, 'accounts/manage_users.html', context)


@login_required
def online_users(request):
    """View online users - only for admin/superuser"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    from datetime import timedelta
    from django.utils import timezone
    
    # Get users who have been active in the last 5 minutes using UserSession for real-time tracking
    time_threshold = timezone.now() - timedelta(minutes=5)
    
    # Get active sessions from the last 5 minutes
    active_sessions = UserSession.objects.filter(
        last_activity__gte=time_threshold,
        user__is_staff=False,
        user__is_superuser=False
    ).values_list('user_id', flat=True).distinct()
    
    # Get the users from active sessions, ordered by their most recent activity
    online_users_list = User.objects.filter(
        id__in=active_sessions
    ).annotate(
        last_activity_time=models.Max('sessions__last_activity')
    ).order_by('-last_activity_time')
    
    # Get total counts
    total_online = online_users_list.count()
    total_students_online = online_users_list.filter(is_professor=False).count()
    total_professors_online = online_users_list.filter(is_professor=True).count()
    
    context = {
        'online_users': online_users_list,
        'total_online': total_online,
        'total_students_online': total_students_online,
        'total_professors_online': total_professors_online,
    }
    return render(request, 'accounts/online_users.html', context)


# Profile View
@login_required
def profile(request):
    """User profile view and edit - Clean version focused on core functionality"""
    if request.method == 'POST':
        # Create a mutable copy of POST data
        post_data = request.POST.copy()
        
        form = ProfileUpdateForm(post_data, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            # If form is invalid, display validation errors via toast
            print(f"Profile update errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
            # Form with errors will be passed to template for inline display
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Get user's resources and bookmarks
    user_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:10]
    user_bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get user achievements (Phase 7)
    user_achievements = request.user.achievements.filter(is_displayed=True).select_related('badge')
    
    # Check for profile completion unlocks
    profile_complete = request.user.check_profile_completion()
    completion_percentage = request.user.get_profile_completion_percentage()

    # Get or create UserStats and UserPreferences
    stats, _ = UserStats.objects.get_or_create(user=request.user)
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)

    # Impact Card Data
    # Get actual quiz count from Quiz model instead of using stats
    from quizzes.models import Quiz
    from resources.models import Rating
    actual_quizzes_count = Quiz.objects.filter(creator=request.user).count()
    
    # Count helpful votes (4-5 star ratings on user's resources)
    helpful_votes = Rating.objects.filter(
        resource__uploader=request.user,
        stars__gte=4
    ).count()
    
    impact_data = {
        'resources_uploaded': stats.resources_uploaded,
        'quizzes_created': actual_quizzes_count,
        'flashcards_created': stats.flashcards_created,
        'students_helped': helpful_votes,
    }

    # Learning Summary Data
    # Calculate study progress based on quiz attempts
    from quizzes.models import QuizAttempt, Quiz
    from flashcards.models import Deck
    
    quiz_attempts_count = QuizAttempt.objects.filter(student=request.user).count()
    # Estimate progress: 0-50 attempts = 0-100% progress
    study_progress_percent = min((quiz_attempts_count / 50) * 100, 100)
    
    # Build combined activity feed from resources, quizzes, and flashcards
    activities = []
    
    # Add resources (uploaded by user)
    for resource in user_resources:
        activities.append({
            'type': 'resource',
            'title': resource.title,
            'created_at': resource.created_at,
            'icon': 'fa-file-alt',
            'color': 'text-secondary',
            'action': 'Uploaded'
        })
    
    # Add quizzes (created by user)
    user_quizzes = Quiz.objects.filter(creator=request.user).order_by('-created_at')[:10]
    for quiz in user_quizzes:
        activities.append({
            'type': 'quiz',
            'title': quiz.title,
            'created_at': quiz.created_at,
            'icon': 'fa-clipboard-check',
            'color': 'text-info',
            'action': 'Created Quiz'
        })
    
    # Add flashcard decks (created by user)
    user_decks = Deck.objects.filter(owner=request.user).order_by('-created_at')[:10]
    for deck in user_decks:
        activities.append({
            'type': 'deck',
            'title': deck.title,
            'created_at': deck.created_at,
            'icon': 'fa-clone',
            'color': 'text-warning',
            'action': 'Created Deck'
        })
    
    # Sort all activities by date and take top 10
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    activities = activities[:10]
    
    learning_summary = {
        'study_progress': round(study_progress_percent, 1),
        'active_streak': stats.active_streak,
        'recent_activities': activities,
        'quizzes_completed': quiz_attempts_count,
    }

    # Achievements & Badges
    achievements = user_achievements

    # Preferences
    customization = {
        'theme': preferences.theme,
        'font_style': preferences.font_style,
        'layout': preferences.layout,
        'dark_mode': preferences.dark_mode,
    }
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def update_profile_picture(request):
    """Handle profile picture upload separately"""
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        try:
            # Update only the profile picture
            request.user.profile_picture = request.FILES['profile_picture']
            request.user.save(update_fields=['profile_picture'])
            messages.success(request, 'Profile picture updated successfully!')
        except Exception as e:
            messages.error(request, f'Error uploading profile picture: {str(e)}')
    else:
        messages.error(request, 'No image file was provided.')
    
    return redirect('accounts:profile')


@login_required
def public_profile(request, username):
    """View another user's public profile (enforcing profile_visibility)"""
    try:
        profile_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('resources:resource_list')
    
    # Check profile visibility
    if profile_user.profile_visibility == 'private':
        # Only the user themselves can see their own private profile
        if request.user != profile_user:
            messages.error(request, 'This profile is private and cannot be accessed.')
            return redirect('resources:resource_list')
    elif profile_user.profile_visibility == 'students_only':
        # Only students (not staff/superuser) can view student-only profiles
        if request.user.is_staff or request.user.is_superuser:
            # Professors and admins are exempt from this restriction
            pass
        elif profile_user.is_staff or profile_user.is_superuser:
            # Staff profiles are always public
            pass
    # 'public' visibility allows everyone to see
    
    # Get public profile data
    profile_resources = Resource.objects.filter(uploader=profile_user, is_public=True).order_by('-created_at')[:10]
    profile_bookmarks = Bookmark.objects.filter(user=profile_user).order_by('-created_at')[:10]
    profile_achievements = profile_user.achievements.filter(is_displayed=True).select_related('badge')
    
    # Get stats
    stats, _ = UserStats.objects.get_or_create(user=profile_user)
    preferences, _ = UserPreferences.objects.get_or_create(user=profile_user)
    
    # Impact Card Data
    from quizzes.models import Quiz, QuizAttempt
    from resources.models import Rating
    actual_quizzes_count = Quiz.objects.filter(creator=profile_user, is_public=True).count()
    helpful_votes = Rating.objects.filter(
        resource__uploader=profile_user,
        resource__is_public=True,
        stars__gte=4
    ).count()
    
    impact_data = {
        'resources_uploaded': Resource.objects.filter(uploader=profile_user, is_public=True).count(),
        'quizzes_created': actual_quizzes_count,
        'flashcards_created': Deck.objects.filter(owner=profile_user, visibility='public').count(),
        'students_helped': helpful_votes,
    }
    
    # Learning Summary Data
    quiz_attempts_count = QuizAttempt.objects.filter(student=profile_user).count()
    study_progress_percent = min((quiz_attempts_count / 50) * 100, 100)
    
    # Build combined activity feed from public resources, quizzes, and flashcards
    activities = []
    
    # Add public resources
    for resource in profile_resources:
        activities.append({
            'type': 'resource',
            'title': resource.title,
            'created_at': resource.created_at,
            'icon': 'fa-file-alt',
            'color': 'text-secondary',
            'action': 'Uploaded'
        })
    
    # Add public quizzes
    user_quizzes = Quiz.objects.filter(creator=profile_user, is_public=True).order_by('-created_at')[:10]
    for quiz in user_quizzes:
        activities.append({
            'type': 'quiz',
            'title': quiz.title,
            'created_at': quiz.created_at,
            'icon': 'fa-clipboard-check',
            'color': 'text-info',
            'action': 'Created Quiz'
        })
    
    # Add public flashcard decks
    user_decks = Deck.objects.filter(owner=profile_user, visibility='public').order_by('-created_at')[:10]
    for deck in user_decks:
        activities.append({
            'type': 'deck',
            'title': deck.title,
            'created_at': deck.created_at,
            'icon': 'fa-clone',
            'color': 'text-warning',
            'action': 'Created Deck'
        })
    
    # Sort all activities by date and take top 10
    activities.sort(key=lambda x: x['created_at'], reverse=True)
    activities = activities[:10]
    
    learning_summary = {
        'study_progress': round(study_progress_percent, 1),
        'active_streak': stats.active_streak,
        'recent_activities': activities,
        'quizzes_completed': quiz_attempts_count,
    }
    
    context = {
        'profile_user': profile_user,
        'user': request.user,
        'user_resources': profile_resources,
        'user_bookmarks': profile_bookmarks,
        'user_achievements': profile_achievements,
        'is_own_profile': request.user == profile_user,
        'impact_data': impact_data,
        'learning_summary': learning_summary,
        'customization': {
            'theme': preferences.theme,
            'font_style': preferences.font_style,
            'layout': preferences.layout,
            'dark_mode': preferences.dark_mode,
        }
    }
    return render(request, 'accounts/public_profile.html', context)


# Password Change View
@login_required
def password_change(request):
    """Password change view with enhanced error handling"""
    must_change = request.user.must_change_password
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Important: Update session to prevent logout
            update_session_auth_hash(request, user)
            
            # Clear the must_change_password flag if it was set
            # Refresh from database to get latest state, then clear the flag
            user.refresh_from_db()
            if user.must_change_password:
                user.must_change_password = False
                user.save(update_fields=['must_change_password'])
                # Also update the request.user object for the middleware check
                request.user.must_change_password = False
            
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('accounts:profile')
        else:
            # Add error messages for better feedback
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'must_change': must_change,
    }
    return render(request, 'accounts/password_change.html', context)


# Default dashboard redirect
@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role"""
    return redirect(request.user.get_dashboard_url())


# Settings View
@login_required
def settings_view(request):
    """Account settings page"""
    if request.method == 'POST':
        # Handle preference updates (Enhanced with AJAX - Phase 7)
        if 'save_preferences' in request.POST:
            from django.http import JsonResponse
            
            default_dashboard = request.POST.get('default_dashboard')
            
            if default_dashboard:
                request.user.default_dashboard = default_dashboard
            
            request.user.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Preferences saved successfully',
                'language_changed': False
            })
        
        # Handle notification preference updates (AJAX)
        if 'update_notification' in request.POST:
            from django.http import JsonResponse
            
            notification_type = request.POST.get('notification_type')
            value = request.POST.get('value') == 'true'
            
            # Map notification types to model fields
            notification_map = {
                'emailNotifications': 'email_notifications',
                'resourceDownloads': 'notify_resource_downloads',
                'quizSubmissions': 'notify_quiz_submissions',
                'systemUpdates': 'notify_system_updates',
                'weeklySummary': 'notify_weekly_summary',
            }
            
            if notification_type in notification_map:
                field_name = notification_map[notification_type]
                setattr(request.user, field_name, value)
                request.user.save()
                return JsonResponse({'success': True, 'message': 'Notification preference updated'})
            
            return JsonResponse({'success': False, 'message': 'Invalid notification type'}, status=400)
        
        # Handle privacy settings (AJAX)
        if 'update_privacy' in request.POST:
            from django.http import JsonResponse
            
            privacy_type = request.POST.get('privacy_type')
            value = request.POST.get('value')
            
            if privacy_type == 'profileVisibility':
                if value in ['public', 'students_only', 'private']:
                    request.user.profile_visibility = value
                    request.user.save()
                    return JsonResponse({'success': True, 'message': 'Privacy settings updated'})
            
            return JsonResponse({'success': False, 'message': 'Invalid privacy setting'}, status=400)
    
    # Check for pending email change request
    from .models import EmailChangeRequest
    pending_email_change = EmailChangeRequest.objects.filter(
        user=request.user, 
        status='pending'
    ).exists()

    context = {
        'user': request.user,
        'dashboard_choices': User.DASHBOARD_CHOICES,
        'language_choices': User.LANGUAGE_CHOICES,
        'visibility_choices': User.VISIBILITY_CHOICES,
        'pending_email_change': pending_email_change,
    }
    return render(request, 'accounts/settings.html', context)


# Change Personal Email View
@login_required
def change_personal_email(request):
    """Change personal email address"""
    from .forms import ChangePersonalEmailForm
    
    if request.method == 'POST':
        form = ChangePersonalEmailForm(request.user, request.POST)
        if form.is_valid():
            # Update the email
            request.user.personal_email = form.cleaned_data['new_email']
            
            # Update backup email
            if 'backup_email' in form.cleaned_data:
                request.user.backup_email = form.cleaned_data['backup_email']
                
            request.user.save()
            
            messages.success(request, 'Your email settings have been updated successfully!')
            return redirect('accounts:settings')
        else:
            # Add error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ChangePersonalEmailForm(request.user)
    
    context = {
        'form': form,
        'email_type': 'personal',
    }
    return render(request, 'accounts/change_email.html', context)


# Change University Email View
@login_required
def change_university_email(request):
    """Change university email address (requires verification)"""
    from .forms import ChangeUniversityEmailForm
    from .models import EmailChangeRequest
    
    # Check for pending requests
    pending_request = EmailChangeRequest.objects.filter(
        user=request.user, 
        status='pending'
    ).first()
    
    if pending_request:
        messages.warning(request, f'You already have a pending request to change your email to {pending_request.new_email}. Please wait for admin approval.')
        return redirect('accounts:settings')
    
    if request.method == 'POST':
        form = ChangeUniversityEmailForm(request.user, request.POST)
        if form.is_valid():
            # Create change request
            EmailChangeRequest.objects.create(
                user=request.user,
                new_email=form.cleaned_data['new_univ_email'],
                reason=form.cleaned_data['reason']
            )
            
            messages.success(request, 'Your request to change university email has been submitted for verification.')
            return redirect('accounts:settings')
        else:
            # Add error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = ChangeUniversityEmailForm(request.user)
    
    context = {
        'form': form,
        'email_type': 'university',
    }
    return render(request, 'accounts/change_email.html', context)


@login_required
def approve_email_request(request, pk):
    """Approve a university email change request"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('resources:moderation_list')
        
    from .models import EmailChangeRequest
    email_request = get_object_or_404(EmailChangeRequest, pk=pk)
    
    if request.method == 'POST':
        email_request.approve(request.user)
        messages.success(request, f'Email change request for {email_request.user.username} approved.')
        
    return redirect('resources:moderation_list')


@login_required
def reject_email_request(request, pk):
    """Reject a university email change request"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('resources:moderation_list')
        
    from .models import EmailChangeRequest
    email_request = get_object_or_404(EmailChangeRequest, pk=pk)
    
    if request.method == 'POST':
        email_request.reject(request.user)
        messages.success(request, f'Email change request for {email_request.user.username} rejected.')
        
    return redirect('resources:moderation_list')


# Phase 7: Advanced Analytics View
@login_required
def analytics_view(request):
    """
    Advanced Analytics page - Unlocked at 100% profile completion.
    Shows detailed statistics and insights.
    """
    # Check if user has access (profile must be 100% complete)
    if not request.user.check_profile_completion():
        messages.warning(request, 'Complete your profile to unlock Advanced Analytics!')
        return redirect('accounts:profile')
    
    from django.db.models import Count, Q
    from datetime import timedelta
    
    # Get user's resources and statistics
    user_resources = Resource.objects.filter(uploader=request.user)
    user_bookmarks = Bookmark.objects.filter(user=request.user)
    
    # Calculate statistics
    total_resources = user_resources.count()
    total_bookmarks = user_bookmarks.count()
    total_views = sum(r.views for r in user_resources)
    
    # Resources by type
    resources_by_type = user_resources.values('resource_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_uploads = user_resources.filter(created_at__gte=thirty_days_ago).count()
    recent_bookmarks = user_bookmarks.filter(created_at__gte=thirty_days_ago).count()
    
    # Most viewed resources
    top_resources = user_resources.order_by('-views')[:5]
    
    # Engagement metrics
    total_downloads = sum(r.downloads for r in user_resources)
    avg_views_per_resource = total_views / total_resources if total_resources > 0 else 0

    # Get or create UserStats
    stats, _ = UserStats.objects.get_or_create(user=request.user)
    
    context = {
        'total_resources': total_resources,
        'total_bookmarks': total_bookmarks,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'avg_views_per_resource': round(avg_views_per_resource, 1),
        'resources_by_type': resources_by_type,
        'recent_uploads': recent_uploads,
        'recent_bookmarks': recent_bookmarks,
        'top_resources': top_resources,
        'stats': stats,
    }
    
    return render(request, 'accounts/analytics.html', context)


# Phase 7: Customization View
@login_required
def customization_view(request):
    """
    Profile Customization page - Unlocked at 100% profile completion.
    Allows users to customize their profile theme and colors.
    """
    # Check if user has access (profile must be 100% complete)
    if not request.user.check_profile_completion():
        messages.warning(request, 'Complete your profile to unlock Profile Customization!')
        return redirect('accounts:profile')
    
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        theme = request.POST.get('theme', preferences.theme)
        font_style = request.POST.get('font_style', preferences.font_style)
        layout = request.POST.get('layout', preferences.layout)
        dark_mode = request.POST.get('dark_mode', 'off') == 'on'
        preferences.theme = theme
        preferences.font_style = font_style
        preferences.layout = layout
        preferences.dark_mode = dark_mode
        preferences.save()
        messages.success(request, 'Customization saved!')
        return redirect('accounts:customization')
    context = {
        'themes': [
            {'name': 'Default', 'primary': '#667eea', 'secondary': '#764ba2'},
            {'name': 'Ocean Blue', 'primary': '#4facfe', 'secondary': '#00f2fe'},
            {'name': 'Sunset', 'primary': '#fa709a', 'secondary': '#fee140'},
            {'name': 'Forest', 'primary': '#43e97b', 'secondary': '#38f9d7'},
            {'name': 'Royal Purple', 'primary': '#8b5cf6', 'secondary': '#7c3aed'},
        ],
        'preferences': preferences,
    }
    return render(request, 'accounts/customization.html', context)


# Session Management Views (Phase 5.3)
@login_required
def view_sessions(request):
    """View all active sessions for the current user"""
    from django.http import JsonResponse
    from .models import UserSession
    
    sessions = UserSession.objects.filter(user=request.user).order_by('-last_activity')
    
    sessions_data = []
    for session in sessions:
        sessions_data.append({
            'id': session.id,
            'device_name': session.device_name,
            'device_type': session.device_type,
            'device_icon': session.get_device_icon(),
            'browser': session.browser,
            'os': session.os,
            'ip_address': session.ip_address,
            'location': session.location or 'Unknown Location',
            'created_at': session.created_at.strftime('%b %d, %Y at %I:%M %p'),
            'last_activity': session.get_time_since_activity(),
            'is_current': session.is_current,
            'is_active': session.is_active(),
        })
    
    return JsonResponse({'success': True, 'sessions': sessions_data})


@login_required
def logout_all_sessions(request):
    """Logout from all devices except the current one"""
    from django.http import JsonResponse
    from django.contrib.sessions.models import Session
    from .models import UserSession
    
    if request.method == 'POST':
        current_session_key = request.session.session_key
        
        # Get all sessions for this user except current
        other_sessions = UserSession.objects.filter(
            user=request.user
        ).exclude(
            session_key=current_session_key
        )
        
        # Delete Django sessions
        for user_session in other_sessions:
            try:
                session = Session.objects.get(session_key=user_session.session_key)
                session.delete()
            except Session.DoesNotExist:
                pass
        
        # Delete UserSession records
        count = other_sessions.count()
        other_sessions.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Successfully logged out from {count} other device(s)'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@login_required
def export_user_data(request):
    """Export all user data as JSON file"""
    import json
    from django.http import HttpResponse
    from datetime import datetime
    
    user = request.user
    
    # Gather all user data
    data = {
        'export_info': {
            'exported_at': datetime.now().isoformat(),
            'export_version': '1.0',
            'user_id': user.id,
        },
        'profile': {
            'username': user.username,
            'email': user.email,
            'personal_email': user.personal_email,
            'univ_email': user.univ_email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'stud_id': user.stud_id,
            'department': user.department,
            'year_level': user.year_level,
            'phone': user.phone,
            'tagline': user.tagline,
            'bio': user.bio,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_professor': user.is_professor,
        },
        'preferences': {
            'default_dashboard': user.default_dashboard,
            'language': user.language,
            'profile_visibility': user.profile_visibility,
        },
        'notifications': {
            'email_notifications': user.email_notifications,
            'notify_resource_downloads': user.notify_resource_downloads,
            'notify_quiz_submissions': user.notify_quiz_submissions,
            'notify_system_updates': user.notify_system_updates,
            'notify_weekly_summary': user.notify_weekly_summary,
            'in_app_sound': user.in_app_sound,
        },
        'resources': [],
        'bookmarks': [],
        'sessions': [],
    }
    
    # Export uploaded resources
    from resources.models import Resource, Bookmark
    resources = Resource.objects.filter(uploader=user).select_related('uploader')
    for resource in resources:
        data['resources'].append({
            'id': resource.id,
            'title': resource.title,
            'description': resource.description,
            'resource_type': resource.resource_type,
            'subject': resource.subject,
            'academic_year': resource.academic_year,
            'semester': resource.semester,
            'views': resource.views,
            'downloads': resource.downloads,
            'verification_status': resource.verification_status,
            'created_at': resource.created_at.isoformat(),
            'updated_at': resource.updated_at.isoformat(),
        })
    
    # Export bookmarks
    bookmarks = Bookmark.objects.filter(user=user).select_related('resource')
    for bookmark in bookmarks:
        data['bookmarks'].append({
            'resource_id': bookmark.resource.id,
            'resource_title': bookmark.resource.title,
            'bookmarked_at': bookmark.created_at.isoformat(),
        })
    
    # Export recent sessions
    from .models import UserSession
    sessions = UserSession.objects.filter(user=user).order_by('-last_activity')[:10]
    for session in sessions:
        data['sessions'].append({
            'device_name': session.device_name,
            'device_type': session.device_type,
            'browser': session.browser,
            'os': session.os,
            'ip_address': session.ip_address,
            'location': session.location,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
        })
    
    # Create JSON response
    json_data = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Create HTTP response with JSON file
    response = HttpResponse(json_data, content_type='application/json')
    filename = f'papertrail_data_{user.username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def delete_account(request):
    """Handle account deletion request"""
    from django.http import JsonResponse
    from datetime import timedelta
    
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '').strip()
        
        # Verify confirmation text
        if confirm_text != 'DELETE':
            return JsonResponse({
                'success': False, 
                'message': 'Confirmation text does not match. Please type DELETE exactly.'
            }, status=400)
        
        user = request.user
        
        # Set deletion request with 7-day grace period
        user.deletion_requested = True
        user.deletion_requested_at = timezone.now()
        user.deletion_scheduled_for = timezone.now() + timedelta(days=7)
        user.save()
        
        # Log out all other sessions
        from django.contrib.sessions.models import Session
        from .models import UserSession
        
        current_session_key = request.session.session_key
        other_sessions = UserSession.objects.filter(user=user).exclude(session_key=current_session_key)
        
        for user_session in other_sessions:
            try:
                session = Session.objects.get(session_key=user_session.session_key)
                session.delete()
            except Session.DoesNotExist:
                pass
        
        other_sessions.delete()
        
        # Log out current user
        from django.contrib.auth import logout
        logout(request)
        
        return JsonResponse({
            'success': True,
            'message': 'Your account deletion has been scheduled. You have 7 days to cancel.',
            'redirect': '/'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@login_required
def cancel_deletion(request):
    """Cancel account deletion request"""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        user = request.user
        
        if not user.deletion_requested:
            return JsonResponse({
                'success': False,
                'message': 'No deletion request found'
            }, status=400)
        
        # Cancel deletion
        user.deletion_requested = False
        user.deletion_requested_at = None
        user.deletion_scheduled_for = None
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Account deletion has been cancelled successfully'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


# ========================================
# API Views for Global Search and Notifications
# ========================================

@login_required
@require_http_methods(["GET"])
def global_search_api(request):
    """Expanded global search across Resources, Quizzes, and Flashcard Decks.
    Matches against title, description, and creator username.
    Returns grouped JSON or 500 with error message on failure."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'resources': [], 'quizzes': [], 'flashcards': []})

    limit = 5  # per category

    try:
        # Resources: title / description / uploader username
        resources = (
            Resource.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(uploader__username__icontains=query)
            )
            .filter(is_public=True)
            .select_related('uploader')
            .order_by('-created_at')[:limit]
        )
        resources_data = [
            {
                'id': r.pk,
                'title': r.title,
                'description': r.description or '',
                'url': reverse('resources:resource_detail', args=[r.pk]),
                'resource_type': r.resource_type,
                'is_verified': r.verification_status == 'verified',
                'author': r.uploader.username,
            }
            for r in resources
        ]

        # Quizzes: title / description / creator username
        quizzes = (
            Quiz.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(creator__username__icontains=query)
            )
            .filter(is_public=True)
            .select_related('creator')
            .order_by('-created_at')[:limit]
        )
        quizzes_data = [
            {
                'id': q.pk,
                'title': q.title,
                'description': q.description or '',
                'url': reverse('quizzes:quiz_detail', args=[q.pk]),
                'is_verified': q.verification_status == 'verified',
                'author': q.creator.username,
            }
            for q in quizzes
        ]

        # Flashcard Decks: title / description / owner username
        decks = (
            Deck.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(owner__username__icontains=query)
            )
            .filter(visibility='public')
            .select_related('owner')
            .order_by('-created_at')[:limit]
        )
        flashcards_data = [
            {
                'id': d.pk,
                'title': d.title,
                'description': d.description or '',
                'url': reverse('flashcards:deck_detail', args=[d.pk]),
                'is_verified': d.verification_status == 'verified',
                'author': d.owner.username,
            }
            for d in decks
        ]

        return JsonResponse(
            {
                'resources': resources_data,
                'quizzes': quizzes_data,
                'flashcards': flashcards_data,
            }
        )
    except Exception as e:
        return JsonResponse({'error': 'Server error', 'detail': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def notifications_unread_count_api(request):
    """
    API endpoint to get unread notification count (role-aware).
    Filters notifications based on user role:
    - Students: new_upload, verification_approved, verification_rejected, new_rating, new_comment
    - Professors: content_review, student_question, new_enrollment + personal notifications
    - Admins: new_user_registration, reported_content, system_alert + personal notifications
    """
    notifications = request.user.notifications.filter(is_read=False)
    
    # Role-based filtering
    if request.user.is_staff:
        # Admins see admin notifications + personal notifications
        admin_types = ['new_user_registration', 'reported_content', 'system_alert']
        personal_types = ['verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=admin_types + personal_types)
    elif request.user.is_professor:
        # Professors see professor notifications + personal notifications
        prof_types = ['content_review', 'student_question', 'new_enrollment']
        personal_types = ['verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=prof_types + personal_types)
    else:
        # Students see student notifications
        student_types = ['new_upload', 'verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=student_types)
    
    count = notifications.count()
    return JsonResponse({'count': count})


@login_required
@require_http_methods(["GET"])
def notifications_list_api(request):
    """
    API endpoint to get user's notifications (latest 20, role-aware).
    Filters notifications based on user role:
    - Students: new_upload, verification_approved, verification_rejected, new_rating, new_comment
    - Professors: content_review, student_question, new_enrollment + personal notifications
    - Admins: new_user_registration, reported_content, system_alert + personal notifications
    """
    notifications = request.user.notifications.all()
    
    # Role-based filtering
    if request.user.is_staff:
        # Admins see admin notifications + personal notifications
        admin_types = ['new_user_registration', 'reported_content', 'system_alert']
        personal_types = ['verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=admin_types + personal_types)
    elif request.user.is_professor:
        # Professors see professor notifications + personal notifications
        prof_types = ['content_review', 'student_question', 'new_enrollment']
        personal_types = ['verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=prof_types + personal_types)
    else:
        # Students see student notifications
        student_types = ['new_upload', 'verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=student_types)
    
    notifications = notifications[:20]
    
    notifications_data = [{
        'id': n.pk,
        'type': n.type,
        'message': n.message,
        'url': n.url or '',
        'is_read': n.is_read,
        'created_at': n.created_at.isoformat()
    } for n in notifications]
    
    return JsonResponse({'notifications': notifications_data})


@login_required
@require_http_methods(["POST"])
def notifications_mark_read_api(request):
    """
    API endpoint to mark a notification as read.
    """
    try:
        data = json.loads(request.body)
        notification_id = data.get('notification_id')
        
        if not notification_id:
            return JsonResponse({'success': False, 'message': 'No notification ID provided'}, status=400)
        
        notification = request.user.notifications.filter(pk=notification_id).first()
        
        if not notification:
            return JsonResponse({'success': False, 'message': 'Notification not found'}, status=404)
        
        notification.mark_as_read()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def notifications_mark_all_read_api(request):
    """
    API endpoint to mark all user notifications as read.
    """
    try:
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def notifications_page(request):
    """
    View all notifications page (role-aware).
    Filters notifications based on user role:
    - Students: new_upload, verification_approved, verification_rejected, new_rating, new_comment
    - Professors: content_review, student_question, new_enrollment + personal notifications
    - Admins: new_user_registration, reported_content, system_alert + personal notifications
    """
    notifications = request.user.notifications.all()
    
    # Role-based filtering
    if request.user.is_staff:
        # Admins see admin notifications + personal notifications
        admin_types = ['new_user_registration', 'reported_content', 'system_alert']
        personal_types = ['verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=admin_types + personal_types)
    elif request.user.is_professor:
        # Professors see professor notifications + personal notifications
        prof_types = ['content_review', 'student_question', 'new_enrollment']
        personal_types = ['verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=prof_types + personal_types)
    else:
        # Students see student notifications
        student_types = ['new_upload', 'verification_approved', 'verification_rejected', 'new_rating', 'new_comment']
        notifications = notifications.filter(type__in=student_types)
    
    context = {
        'notifications': notifications
    }
    
    return render(request, 'accounts/notifications.html', context)


@login_required
def global_search_page(request):
    """Full-page global search results view.
    Provides expanded result lists beyond dropdown preview.
    """
    query = request.GET.get('q', '').strip()
    resources_data = quizzes_data = flashcards_data = []
    total_counts = {'resources': 0, 'quizzes': 0, 'flashcards': 0}

    if query:
        # Larger limit for full page
        limit = 50
        # Resources
        resources = (
            Resource.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(uploader__username__icontains=query)
            )
            .filter(is_public=True)
            .select_related('uploader')
            .order_by('-created_at')[:limit]
        )
        resources_data = resources
        total_counts['resources'] = resources.count()

        # Quizzes
        quizzes = (
            Quiz.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(creator__username__icontains=query)
            )
            .filter(is_public=True)
            .select_related('creator')
            .order_by('-created_at')[:limit]
        )
        quizzes_data = quizzes
        total_counts['quizzes'] = quizzes.count()

        # Flashcards (Decks)
        decks = (
            Deck.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(owner__username__icontains=query)
            )
            .filter(visibility='public')
            .select_related('owner')
            .order_by('-created_at')[:limit]
        )
        flashcards_data = decks
        total_counts['flashcards'] = decks.count()

    context = {
        'query': query,
        'resources': resources_data,
        'quizzes': quizzes_data,
        'flashcards': flashcards_data,
        'total_counts': total_counts,
    }
    return render(request, 'search/global_search_results.html', context)


@login_required
def ban_user(request, user_id):
    """Ban a user - admin only"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:manage_users')
    
    try:
        user_to_ban = User.objects.get(id=user_id)
        if user_to_ban == request.user:
            messages.error(request, 'You cannot ban yourself.')
            return redirect('accounts:manage_users')
        
        user_to_ban.is_banned = True
        user_to_ban.save(update_fields=['is_banned'])
        messages.success(request, f'{user_to_ban.get_display_name()} has been banned.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('accounts:manage_users')


@login_required
def unban_requests(request):
    """View and manage unban requests - admin only"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:admin_dashboard')
    
    # Get all banned users
    banned_users = User.objects.filter(is_banned=True, is_staff=False, is_superuser=False).order_by('-date_joined')
    
    context = {
        'banned_users': banned_users,
        'total_banned': banned_users.count(),
    }
    
    return render(request, 'accounts/unban_requests.html', context)


@login_required
def unban_user(request, user_id):
    """Unban a user - admin only"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:unban_requests')
    
    try:
        user_to_unban = User.objects.get(id=user_id)
        user_to_unban.is_banned = False
        user_to_unban.save(update_fields=['is_banned'])
        messages.success(request, f'{user_to_unban.get_display_name()} has been unbanned.')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('accounts:unban_requests')


# ========================================
# Password Reset Views
# ========================================

def forgot_password_step1(request):
    """Step 1: User enters their Student ID and chooses reset method"""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    if request.method == 'POST':
        stud_id = request.POST.get('stud_id', '').strip()
        method = request.POST.get('method', 'email')
        
        try:
            user = User.objects.get(stud_id=stud_id)
            
            if method == 'email':
                # Email method - create reset token and send via email
                reset_token = PasswordResetToken.create_for_user(user)
                
                # Send verification code via email
                try:
                    from django.conf import settings
                    from django.core.mail import send_mail
                    import logging
                    
                    logger = logging.getLogger(__name__)
                    
                    recipient_email = user.personal_email or user.univ_email
                    logger.info(f'Attempting to send reset code to: {recipient_email}')
                    logger.info(f'Email backend: {settings.EMAIL_BACKEND}')
                    logger.info(f'Email host user: {settings.EMAIL_HOST_USER}')
                    
                    if recipient_email:
                        subject = 'Your Password Reset Code - PaperTrail'
                        message = f'''Hello {user.get_display_name()},

Your password reset verification code is: {reset_token.token}

This code will expire in 15 minutes. Do not share this code with anyone.

If you did not request this password reset, please ignore this email.

Best regards,
PaperTrail Team'''
                        
                        # Send email synchronously so we can see the error
                        result = send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [recipient_email],
                            fail_silently=False,
                        )
                        
                        logger.info(f'Email sent successfully. Result: {result}')
                        messages.success(request, f'A verification code has been sent to {recipient_email}.')
                    else:
                        logger.error(f'No email found for user {user.stud_id}. Personal: {user.personal_email}, Univ: {user.univ_email}')
                        messages.error(request, 'No email address found in your account.')
                        return redirect('accounts:forgot_password_step1')
                
                except Exception as e:
                    logger.error(f'Email sending failed: {str(e)}', exc_info=True)
                    messages.error(request, f'Failed to send email: {str(e)}')
                    return redirect('accounts:forgot_password_step1')
                
                request.session['reset_user_id'] = user.id
                request.session['reset_method'] = 'email'
                request.session['reset_code_sent'] = True
                
                return redirect('accounts:forgot_password_step2')
            
            elif method == 'admin':
                # Admin method - create request and notify admin
                reset_token = PasswordResetToken.create_for_user(user)
                
                # Create a password reset request for admin to review
                reset_request = PasswordResetRequest.objects.create(
                    user=user,
                    contact_info=user.personal_email or user.univ_email or 'No email provided',
                    status='pending'
                )
                
                # Create notification for all admins
                admin_users = User.objects.filter(is_staff=True, is_superuser=True)
                for admin in admin_users:
                    Notification.objects.create(
                        user=admin,
                        type='password_reset_request',
                        message=f'{user.get_display_name()} ({user.stud_id}) has requested a password reset.',
                        url=reverse('accounts:admin_dashboard'),
                        related_object_type='PasswordResetRequest',
                        related_object_id=reset_request.id
                    )
                
                request.session['reset_user_id'] = user.id
                request.session['reset_method'] = 'admin'
                request.session['reset_request_id'] = reset_request.id
                
                messages.success(
                    request, 
                    f'Admin has been notified. Please wait for their approval.'
                )
                return redirect('accounts:forgot_password_step2')
        
        except User.DoesNotExist:
            messages.error(request, 'Student ID not found. Please check and try again.')
    
    return render(request, 'accounts/forgot_password_step1.html')


def forgot_password_step2(request):
    """Step 2: Email code verification OR wait for admin approval"""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    # Check if user came from step 1
    reset_user_id = request.session.get('reset_user_id')
    reset_method = request.session.get('reset_method')
    reset_request_id = request.session.get('reset_request_id')
    
    if not reset_user_id:
        messages.error(request, 'Please start from the beginning.')
        return redirect('accounts:forgot_password_step1')
    
    try:
        user = User.objects.get(id=reset_user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('accounts:forgot_password_step1')
    
    # Handle admin method - check if admin has approved
    if reset_method == 'admin':
        # Check if admin approved the request
        if reset_request_id:
            try:
                reset_request = PasswordResetRequest.objects.get(id=reset_request_id)
                if reset_request.status == 'approved':
                    # Admin approved, mark as verified and proceed to step 3
                    request.session['reset_verified'] = True
                    messages.success(request, 'Admin has approved! Now set your new password.')
                    return redirect('accounts:forgot_password_step3')
            except PasswordResetRequest.DoesNotExist:
                pass
        
        # Still waiting for admin approval
        context = {
            'user_display': user.get_display_name(),
            'reset_method': reset_method,
            'is_waiting_for_admin': True,
        }
        return render(request, 'accounts/forgot_password_step2.html', context)
    
    # Handle email method - verify code
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        try:
            reset_token = PasswordResetToken.objects.get(user=user, token=code)
            
            # Check if token is valid
            if not reset_token.is_valid():
                messages.error(request, 'Code has expired. Please try again.')
                return redirect('accounts:forgot_password_step1')
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Store verification status in session
            request.session['reset_verified'] = True
            
            messages.success(request, 'Code verified! Now set your new password.')
            return redirect('accounts:forgot_password_step3')
        except PasswordResetToken.DoesNotExist:
            messages.error(request, 'Invalid code. Please try again.')
    
    context = {
        'user_display': user.get_display_name(),
        'reset_method': reset_method,
        'is_waiting_for_admin': False,
    }
    return render(request, 'accounts/forgot_password_step2.html', context)


def forgot_password_step3(request):
    """Step 3: User sets new password"""
    if request.user.is_authenticated:
        return redirect(request.user.get_dashboard_url())
    
    # Check if user verified the code
    reset_user_id = request.session.get('reset_user_id')
    reset_verified = request.session.get('reset_verified')
    reset_method = request.session.get('reset_method')
    reset_request_id = request.session.get('reset_request_id')
    
    if not reset_user_id or not reset_verified:
        messages.error(request, 'Please complete the verification steps first.')
        return redirect('accounts:forgot_password_step1')
    
    try:
        user = User.objects.get(id=reset_user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('accounts:forgot_password_step1')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        
        # Validate passwords
        if not password1 or not password2:
            messages.error(request, 'Both password fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            # Update password
            user.set_password(password1)
            user.save()
            
            # If admin method, mark the request as completed
            if reset_method == 'admin' and reset_request_id:
                try:
                    reset_request = PasswordResetRequest.objects.get(id=reset_request_id)
                    reset_request.status = 'completed'
                    reset_request.save()
                except PasswordResetRequest.DoesNotExist:
                    pass
            
            # Clear session
            for key in ['reset_user_id', 'reset_verified', 'reset_code_sent', 'reset_method', 'reset_request_id']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, 'Password reset successful! You can now log in.')
            return redirect('accounts:login')
    
    context = {
        'user_display': user.get_display_name(),
        'reset_method': reset_method,
    }
    return render(request, 'accounts/forgot_password_step3.html', context)


@login_required
def admin_send_password_reset(request):
    """Admin sends password reset code to a user"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:admin_dashboard')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            
            # Create password reset token
            reset_token = PasswordResetToken.create_for_user(user)
            
            # TODO: Send code via email
            messages.success(request, f'Password reset code sent to {user.get_display_name()}.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
    
    return redirect('accounts:manage_users')


@login_required
def approve_password_reset(request, pk):
    """Admin approves a password reset request"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:admin_dashboard')
    
    try:
        reset_request = PasswordResetRequest.objects.get(id=pk)
        reset_request.status = 'approved'
        reset_request.approved_by = request.user
        reset_request.save()
        
        messages.success(request, f'Password reset request for {reset_request.user.get_display_name()} has been approved.')
    except PasswordResetRequest.DoesNotExist:
        messages.error(request, 'Password reset request not found.')
    
    return redirect('accounts:admin_dashboard')


@login_required
def deny_password_reset(request, pk):
    """Admin denies a password reset request"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:admin_dashboard')
    
    try:
        reset_request = PasswordResetRequest.objects.get(id=pk)
        reset_request.status = 'denied'
        reset_request.approved_by = request.user
        reset_request.save()
        
        messages.success(request, f'Password reset request for {reset_request.user.get_display_name()} has been denied.')
    except PasswordResetRequest.DoesNotExist:
        messages.error(request, 'Password reset request not found.')
    
    return redirect('accounts:admin_dashboard')
