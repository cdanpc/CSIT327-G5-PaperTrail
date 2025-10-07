from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm as CustomUserCreationForm, AuthenticationForm as CustomAuthenticationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

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

class CustomLoginView(LoginView):
    """Custom login view"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        """Handle successful login"""
        user = form.get_user()
        login(self.request, user)
        
        messages.success(self.request, f'Welcome back, {user.get_display_name()}!')
        return redirect('accounts:student_dashboard')
    
@login_required
def dashboard(request):
    """User dashboard"""
    user = request.user
    return render(request, 'accounts/student_dashboard.html', {'user': user})


@login_required
def profile(request):
    """User profile page"""
    user = request.user
    
    return render(request, 'accounts/profile.html')
