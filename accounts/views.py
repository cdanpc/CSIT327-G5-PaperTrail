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
from .models import User
from resources.models import Resource, Bookmark
from quizzes.models import QuizAttempt


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
    
    # Get user's recent resources and bookmarks
    recent_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:5]
    recent_bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Phase 8: Profile completion integration
    profile_completion = request.user.get_profile_completion_percentage()
    profile_complete = request.user.check_profile_completion()
    
    # Get total counts for stats
    total_resources = Resource.objects.filter(uploader=request.user).count()
    total_bookmarks = Bookmark.objects.filter(user=request.user).count()
    quizzes_completed = QuizAttempt.objects.filter(student=request.user, completed_at__isnull=False).count()
    
    context = {
        'user': request.user,
        'recent_resources': recent_resources,
        'recent_bookmarks': recent_bookmarks,
        'profile_completion': profile_completion,
        'profile_complete': profile_complete,
        'total_resources': total_resources,
        'total_bookmarks': total_bookmarks,
        'quizzes_completed': quizzes_completed,
    }
    return render(request, 'accounts/student_dashboard.html', context)


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
    
    # Get professor's uploaded resources
    professor_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:5]
    
    # Get recently verified resources by this professor
    recently_verified = Resource.objects.filter(
        verification_by=request.user,
        verification_status='verified'
    ).order_by('-verified_at')[:5]
    
    context = {
        'user': request.user,
        'pending_verifications': pending_verifications,
        'professor_resources': professor_resources,
        'recently_verified': recently_verified,
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
    
    context = {
        'form': form,
        'user': request.user,
        'user_resources': user_resources,
        'user_bookmarks': user_bookmarks,
        'user_achievements': user_achievements,
        'profile_complete': profile_complete,
        'completion_percentage': completion_percentage,
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
    
    if request.method == 'POST':
        # Handle theme customization (to be implemented with user preferences model)
        messages.success(request, 'Customization saved! (Feature coming soon)')
        return redirect('accounts:customization')
    
    context = {
        'themes': [
            {'name': 'Default', 'primary': '#667eea', 'secondary': '#764ba2'},
            {'name': 'Ocean Blue', 'primary': '#4facfe', 'secondary': '#00f2fe'},
            {'name': 'Sunset', 'primary': '#fa709a', 'secondary': '#fee140'},
            {'name': 'Forest', 'primary': '#43e97b', 'secondary': '#38f9d7'},
            {'name': 'Royal Purple', 'primary': '#8b5cf6', 'secondary': '#7c3aed'},
        ]
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
