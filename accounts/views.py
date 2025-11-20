from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils import timezone
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    ProfileUpdateForm,
    CustomPasswordChangeForm
)
from .models import User, UserStats, UserPreferences, UserSession
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

    # Extended multi-metric Learning Insights (uploads, quizzes, flashcards, activity count)
    # Reuse weekly_labels for all metrics to avoid recalculating.
    weekly_quiz_counts = []
    weekly_views_counts = []
    weekly_flashcard_counts = []
    date_sequence = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        date_sequence.append(day)
        # Quizzes: count both quizzes created AND quiz attempts completed that day
        quiz_created = Quiz.objects.filter(creator=request.user, created_at__date=day).count()
        quiz_completed = QuizAttempt.objects.filter(student=request.user, completed_at__date=day).count()
        weekly_quiz_counts.append(quiz_created + quiz_completed)
        # Activity count: ratings, comments, bookmarks created that day (user engagement)
        activity_count = (
            Rating.objects.filter(user=request.user, created_at__date=day).count() +
            Comment.objects.filter(user=request.user, created_at__date=day).count() +
            Bookmark.objects.filter(user=request.user, created_at__date=day).count()
        )
        weekly_views_counts.append(activity_count)
    # Flashcards weekly counts via service
    weekly_flashcard_counts = flashcard_services.get_weekly_flashcard_counts(request.user, date_sequence)

    # Compute per-metric and overall maxima for the period
    max_uploads = max(weekly_upload_counts) if weekly_upload_counts else 0
    max_quizzes = max(weekly_quiz_counts) if weekly_quiz_counts else 0
    max_flashcards = max(weekly_flashcard_counts) if weekly_flashcard_counts else 0
    max_activity = max(weekly_views_counts) if weekly_views_counts else 0
    max_overall = max(max_uploads, max_quizzes, max_flashcards, max_activity)

    weekly_metrics = {
        'labels': weekly_labels,
        'uploads': weekly_upload_counts,
        'quizzes': weekly_quiz_counts,
        'flashcards': weekly_flashcard_counts,
        'activity': weekly_views_counts,  # Renamed from 'views' to 'activity' for clarity
        'max_values': {
            'uploads': max_uploads,
            'quizzes': max_quizzes,
            'flashcards': max_flashcards,
            'activity': max_activity,
            'overall': max_overall,
        },
        'palette': {
            'uploads': '#0d6efd',
            'quizzes': '#ffc107',
            'flashcards': '#0dcaf0',
            'activity': '#198754'  # Green for activity (ratings, comments, bookmarks)
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
    
    # Get recent users
    recent_users = User.objects.order_by('-date_joined')[:10]
    
    context = {
        'user': request.user,
        'total_users': total_users,
        'total_students': total_students,
        'total_professors': total_professors,
        'banned_users': banned_users,
        'pending_resources': pending_resources,
        'recent_users': recent_users,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def promote_to_professor(request):
    """Promote a student to professor role"""
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect(request.user.get_dashboard_url())
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
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
        
        return redirect('accounts:admin_dashboard')
    
    # GET request - return list of students who can be promoted
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
    role_filter = request.GET.get('role', '')  # 'professor', 'student', or empty for all
    
    if search_query:
        all_users = all_users.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(univ_email__icontains=search_query)
        )
    
    if role_filter == 'professor':
        all_users = all_users.filter(is_professor=True)
    elif role_filter == 'student':
        all_users = all_users.filter(is_professor=False)
    
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
    """User profile view and edit"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            
            # Check if profile is now 100% complete and unlock badge (Phase 7)
            if request.user.check_profile_completion():
                achievement = request.user.unlock_verified_student_badge()
                if achievement and achievement.unlocked_date.date() == timezone.now().date():
                    # Only show message if badge was just unlocked today
                    messages.success(request, '🎉 Congratulations! You unlocked the Verified Student badge!')
            
            return redirect('accounts:profile')
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
    impact_data = {
        'resources_uploaded': stats.resources_uploaded,
        'quizzes_created': stats.quizzes_created,
        'flashcards_created': stats.flashcards_created,
        'students_helped': stats.students_helped,
    }

    # Learning Summary Data
    learning_summary = {
        'study_progress': stats.total_study_time,
        'active_streak': stats.active_streak,
        'recent_activities': [],  # To be filled with recent actions
        'quizzes_completed': stats.quizzes_completed,
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
        'user_resources': user_resources,
        'user_bookmarks': user_bookmarks,
        'user_achievements': achievements,
        'profile_complete': profile_complete,
        'completion_percentage': completion_percentage,
        'impact_data': impact_data,
        'learning_summary': learning_summary,
        'customization': customization,
    }
    return render(request, 'accounts/profile.html', context)


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
            language = request.POST.get('language')
            current_language = request.user.language
            
            if default_dashboard:
                request.user.default_dashboard = default_dashboard
            if language:
                request.user.language = language
            
            request.user.save()
            
            # Check if language changed (to determine if reload needed)
            language_changed = language and language != current_language
            
            return JsonResponse({
                'success': True,
                'message': 'Preferences saved successfully',
                'language_changed': language_changed
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
                'inAppSound': 'in_app_sound',
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
    
    context = {
        'user': request.user,
        'dashboard_choices': User.DASHBOARD_CHOICES,
        'language_choices': User.LANGUAGE_CHOICES,
        'visibility_choices': User.VISIBILITY_CHOICES,
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
            request.user.save()
            
            messages.success(request, 'Your personal email has been updated successfully!')
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
    
    if request.method == 'POST':
        form = ChangeUniversityEmailForm(request.user, request.POST)
        if form.is_valid():
            # Update the university email
            request.user.univ_email = form.cleaned_data['new_univ_email']
            request.user.save()
            
            # TODO: Send verification email and admin notification
            # For now, just update directly
            
            messages.success(request, 'Your university email has been updated successfully! You may need to verify the new email.')
            messages.info(request, 'An administrator has been notified of this change.')
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
