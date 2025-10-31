from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from user_agents import parse


class ForcePasswordChangeMiddleware:
    """Middleware to force users to change password when required"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is logged in and needs to change password
        if (request.user.is_authenticated and 
            request.user.must_change_password):
            
            # Allow access to password change page and logout
            allowed_paths = [
                '/accounts/password-change/',
                '/accounts/logout/',
                '/admin/logout/',  # Django admin logout
                '/static/',  # Allow static files
                '/media/',  # Allow media files
            ]
            
            # Check if current path is not in allowed paths
            if not any(request.path.startswith(path) for path in allowed_paths):
                messages.warning(request, 'For security reasons, you must change your password before continuing.')
                return redirect('accounts:password_change')
        
        response = self.get_response(request)
        return response


class UserRoleMiddleware:
    """Middleware to handle role-based access control"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Add role context to all requests
            request.user_role = request.user.get_role()
            
            # Admin-only paths
            admin_paths = ['/accounts/dashboard/admin/']
            if (not request.user.is_staff and 
                not request.user.is_superuser and 
                any(request.path.startswith(path) for path in admin_paths)):
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('accounts:dashboard')
            
            # Professor-only paths
            professor_paths = ['/accounts/dashboard/professor/']
            if (not request.user.is_professor and 
                any(request.path.startswith(path) for path in professor_paths)):
                messages.error(request, 'Access denied. Professor privileges required.')
                return redirect('accounts:dashboard')
            
            # Check if user is banned
            if request.user.is_banned:
                # Allow only logout
                if not request.path.startswith('/accounts/logout/'):
                    messages.error(request, 'Your account has been banned. Please contact support.')
                    return redirect('accounts:logout')
        
        response = self.get_response(request)
        return response


class SessionTrackingMiddleware:
    """Middleware to track user sessions across devices"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated and request.session.session_key:
            self._track_session(request)
        
        response = self.get_response(request)
        return response
    
    def _track_session(self, request):
        """Track or update user session"""
        from .models import UserSession
        
        session_key = request.session.session_key
        
        # Get or create session record
        session, created = UserSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user': request.user,
                'ip_address': self._get_client_ip(request),
                'device_name': self._get_device_name(request),
                'device_type': self._get_device_type(request),
                'browser': self._get_browser(request),
                'os': self._get_os(request),
                'is_current': True,
            }
        )
        
        # Update existing session
        if not created:
            session.last_activity = timezone.now()
            session.is_current = True
            session.save(update_fields=['last_activity', 'is_current'])
        
        # Mark all other sessions as not current
        UserSession.objects.filter(
            user=request.user
        ).exclude(
            session_key=session_key
        ).update(is_current=False)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
    
    def _get_device_name(self, request):
        """Get device name from user agent"""
        try:
            user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
            browser = user_agent.browser.family
            os = user_agent.os.family
            return f"{browser} on {os}"
        except:
            return "Unknown Device"
    
    def _get_device_type(self, request):
        """Get device type (mobile, tablet, desktop)"""
        try:
            user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
            if user_agent.is_mobile:
                return 'mobile'
            elif user_agent.is_tablet:
                return 'tablet'
            else:
                return 'desktop'
        except:
            return 'desktop'
    
    def _get_browser(self, request):
        """Get browser name"""
        try:
            user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
            return f"{user_agent.browser.family} {user_agent.browser.version_string}"
        except:
            return "Unknown Browser"
    
    def _get_os(self, request):
        """Get operating system"""
        try:
            user_agent = parse(request.META.get('HTTP_USER_AGENT', ''))
            return f"{user_agent.os.family} {user_agent.os.version_string}"
        except:
            return "Unknown OS"
