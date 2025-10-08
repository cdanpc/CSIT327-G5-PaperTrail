from django.urls import path
from django.contrib.auth.views import PasswordResetView
from . import views

app_name = 'accounts'

urlpatterns = [
    # User Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # Password Management
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),

    # User Dashboard and Profile
    path('dashboard/', views.dashboard, name='dashboard'),
]