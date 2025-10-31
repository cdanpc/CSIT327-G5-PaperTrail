from django.urls import path
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/professor/', views.professor_dashboard, name='professor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('password-change/', views.password_change, name='password_change'),
    path('change-personal-email/', views.change_personal_email, name='change_personal_email'),
    path('change-university-email/', views.change_university_email, name='change_university_email'),
    
    # Session Management (Phase 5.3)
    path('sessions/view/', views.view_sessions, name='view_sessions'),
    path('sessions/logout-all/', views.logout_all_sessions, name='logout_all_sessions'),
    
    # Phase 7: Completion Unlocks
    path('analytics/', views.analytics_view, name='analytics'),
    path('customization/', views.customization_view, name='customization'),
    
    # Session Management & Data Export (Phase 5)
    path('sessions/view/', views.view_sessions, name='view_sessions'),
    path('sessions/logout-all/', views.logout_all_sessions, name='logout_all_sessions'),
    path('export-data/', views.export_user_data, name='export_data'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('cancel-deletion/', views.cancel_deletion, name='cancel_deletion'),
    
    # Forgot Password (Link-based reset - Standard method) - TEMP DISABLED
    # path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    # path('reset/<str:token>/', views.reset_password_token, name='reset_password_token'),
    
    # Old verification code routes (deprecated, keeping for backward compatibility) - TEMP DISABLED
    # path('verify-code/<int:token_id>/', views.verify_code, name='verify_code'),
    # path('reset-password/<int:token_id>/', views.reset_password, name='reset_password'),
    
    # Password Reset (Old Django default - keeping for compatibility)
    path('password-reset/', 
         PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]