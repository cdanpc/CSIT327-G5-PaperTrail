from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    ProfileUpdateForm,
    CustomPasswordChangeForm
)
from .models import User
from resources.models import Resource, Bookmark


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
    
    context = {
        'user': request.user,
        'recent_resources': recent_resources,
        'recent_bookmarks': recent_bookmarks,
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
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    # Get user's resources and bookmarks
    user_resources = Resource.objects.filter(uploader=request.user).order_by('-created_at')[:10]
    user_bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'user': request.user,
        'user_resources': user_resources,
        'user_bookmarks': user_bookmarks,
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