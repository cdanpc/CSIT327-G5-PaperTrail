# Import all views to maintain backward compatibility
from .auth import RegisterView, login_view, logout_view
from .dashboard import student_dashboard, professor_dashboard, admin_dashboard
from .study_reminders import add_study_reminder, toggle_study_reminder, delete_study_reminder

__all__ = [
    # Auth
    'RegisterView', 'login_view', 'logout_view',
    # Dashboard
    'student_dashboard', 'professor_dashboard', 'admin_dashboard',
    # Study Reminders
    'add_study_reminder', 'toggle_study_reminder', 'delete_study_reminder',
]
