# Import all views from the views.py file to maintain backward compatibility
import sys
import importlib.util
import os

# The views.py file is in the parent directory
# We need to load it explicitly since we're in a views/ package
spec = importlib.util.spec_from_file_location(
    "accounts._views_file",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'views.py')
)
parent_views = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent_views)

profile = parent_views.profile
update_profile_picture = parent_views.update_profile_picture
public_profile = parent_views.public_profile
password_change = parent_views.password_change
settings_view = parent_views.settings_view
change_personal_email = parent_views.change_personal_email
change_university_email = parent_views.change_university_email
analytics_view = parent_views.analytics_view
customization_view = parent_views.customization_view
view_sessions = parent_views.view_sessions
logout_all_sessions = parent_views.logout_all_sessions
export_user_data = parent_views.export_user_data
delete_account = parent_views.delete_account
cancel_deletion = parent_views.cancel_deletion
promote_to_professor = parent_views.promote_to_professor
demote_professor = parent_views.demote_professor
manage_users = parent_views.manage_users
online_users = parent_views.online_users
ban_user = parent_views.ban_user
unban_requests = parent_views.unban_requests
unban_user = parent_views.unban_user
global_search_api = parent_views.global_search_api
notifications_unread_count_api = parent_views.notifications_unread_count_api
notifications_list_api = parent_views.notifications_list_api
notifications_mark_read_api = parent_views.notifications_mark_read_api
notifications_mark_all_read_api = parent_views.notifications_mark_all_read_api
notifications_page = parent_views.notifications_page
global_search_page = parent_views.global_search_page
dashboard = parent_views.dashboard
forgot_password_step1 = parent_views.forgot_password_step1
forgot_password_step2 = parent_views.forgot_password_step2
forgot_password_step3 = parent_views.forgot_password_step3
admin_send_password_reset = parent_views.admin_send_password_reset
approve_password_reset = parent_views.approve_password_reset
deny_password_reset = parent_views.deny_password_reset

__all__ = [
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
]
