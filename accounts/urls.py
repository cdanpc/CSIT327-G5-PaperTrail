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
    
    # Admin Role Management
    path('admin/promote-professor/', views.promote_to_professor, name='promote_to_professor'),
    path('admin/demote-professor/<int:user_id>/', views.demote_professor, name='demote_professor'),
    path('admin/manage-users/', views.manage_users, name='manage_users'),
    path('admin/online-users/', views.online_users, name='online_users'),
    path('admin/ban-user/<int:user_id>/', views.ban_user, name='ban_user'),
    path('admin/unban-requests/', views.unban_requests, name='unban_requests'),
    path('admin/unban-user/<int:user_id>/', views.unban_user, name='unban_user'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
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
         views.forgot_password_step1,
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
    
    # New Password Reset Flow (Student ID + Verification Code)
    path('forgot-password/step1/', views.forgot_password_step1, name='forgot_password_step1'),
    path('forgot-password/step2/', views.forgot_password_step2, name='forgot_password_step2'),
    path('forgot-password/step3/', views.forgot_password_step3, name='forgot_password_step3'),
    
    # Admin Password Reset
    path('admin/send-password-reset/<int:user_id>/', views.admin_send_password_reset, name='admin_send_password_reset'),
    path('admin/approve-password-reset/<int:pk>/', views.approve_password_reset, name='approve_password_reset'),
    path('admin/deny-password-reset/<int:pk>/', views.deny_password_reset, name='deny_password_reset'),
]