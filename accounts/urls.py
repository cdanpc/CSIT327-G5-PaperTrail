from django.urls import path
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views
from .forms import CITPasswordResetForm, CITSetPasswordForm

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
    
    # Notifications
    path('notifications/', views.notifications_page, name='notifications'),
    
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
    
    # Study Reminders
    path('reminders/add/', views.add_study_reminder, name='add_study_reminder'),
    path('reminders/toggle/<int:pk>/', views.toggle_study_reminder, name='toggle_study_reminder'),
    path('reminders/delete/<int:pk>/', views.delete_study_reminder, name='delete_study_reminder'),
    
    # Forgot Password - Django Built-in Views with @cit.edu Validation
    path('forgot-password/', 
         PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.txt',
             subject_template_name='registration/password_reset_subject.txt',
             form_class=CITPasswordResetForm,
             success_url='/accounts/forgot-password/done/'
         ), 
         name='password_reset'),
    path('forgot-password/done/', 
         PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             form_class=CITSetPasswordForm,
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]