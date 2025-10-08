from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


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
