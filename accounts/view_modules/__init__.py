# Import all views to maintain backward compatibility
from .auth import RegisterView, login_view, logout_view
from .dashboard import student_dashboard, professor_dashboard, admin_dashboard
from .study_reminders import add_study_reminder, toggle_study_reminder, delete_study_reminder

# Import the rest from parent views.py file (no conflict now that folder is renamed)
from accounts.views import (
    profile, update_profile_picture, public_profile, password_change,
    settings_view, change_personal_email, change_university_email,
    analytics_view, customization_view, view_sessions, logout_all_sessions,
    export_user_data, delete_account, cancel_deletion,
    promote_to_professor, demote_professor, manage_users, online_users,
    ban_user, unban_requests, unban_user,
    global_search_api, notifications_unread_count_api, notifications_list_api,
    notifications_mark_read_api, notifications_mark_all_read_api,
    notifications_page, global_search_page, dashboard,
    forgot_password_step1, forgot_password_step2, forgot_password_step3,
    admin_send_password_reset, approve_password_reset, deny_password_reset,
)

__all__ = [
    # Auth
    'RegisterView', 'login_view', 'logout_view',
    # Dashboard
    'student_dashboard', 'professor_dashboard', 'admin_dashboard',
    # Profile
    'profile', 'update_profile_picture', 'public_profile', 'password_change',
    # Settings
    'settings_view', 'change_personal_email', 'change_university_email',
    'analytics_view', 'customization_view', 'view_sessions', 'logout_all_sessions',
    'export_user_data', 'delete_account', 'cancel_deletion',
    # Admin
    'promote_to_professor', 'demote_professor', 'manage_users', 'online_users',
    'ban_user', 'unban_requests', 'unban_user',
    # API
    'global_search_api', 'notifications_unread_count_api', 'notifications_list_api',
    'notifications_mark_read_api', 'notifications_mark_all_read_api',
    # Pages
    'notifications_page', 'global_search_page', 'dashboard',
    # Password Reset
    'forgot_password_step1', 'forgot_password_step2', 'forgot_password_step3',
    'admin_send_password_reset', 'approve_password_reset', 'deny_password_reset',
    # Study Reminders
    'add_study_reminder', 'toggle_study_reminder', 'delete_study_reminder',
]
