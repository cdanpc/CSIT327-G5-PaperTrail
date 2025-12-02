from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from ..forms import CustomUserCreationForm, CustomAuthenticationForm


class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Handle successful registration"""
        try:
            user = form.save()
            messages.success(self.request, 'Account created successfully! Please log in.')
            return redirect(self.success_url)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Registration error: {e}", exc_info=True)
            messages.error(self.request, 'An error occurred during registration. Please try again.')
            return self.form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(request.user.get_dashboard_url())
        return super().dispatch(request, *args, **kwargs)


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
                
                if user.must_change_password:
                    messages.warning(request, 'You must change your password.')
                    return redirect('accounts:password_change')
                
                return redirect(user.get_dashboard_url())
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout user and redirect to landing page"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
