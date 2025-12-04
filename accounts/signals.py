"""
Signals for accounts app notifications
Handles: new user registrations (for admins)
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse

from .models import Notification

User = get_user_model()


@receiver(post_save, sender=User)
def notify_admins_new_user_registration(sender, instance, created, **kwargs):
    """
    Notify all admins when a new user registers.
    Triggered when: A new User is created
    """
    if created:
        try:
            # Get all admin users (superusers and staff)
            admins = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
            
            # Determine role display
            if instance.is_superuser or instance.is_staff:
                role = 'Admin'
            elif instance.is_professor:
                role = 'Professor'
            else:
                role = 'Student'
            
            # Create notifications for all admins
            notifications = [
                Notification(
                    user=admin,
                    type='new_user_registration',
                    message=f"New user registered: {instance.get_display_name()} (Role: {role})",
                    url=reverse('accounts:manage_users') if admin != instance else reverse('accounts:profile'),
                    related_object_type='user',
                    related_object_id=instance.id
                )
                for admin in admins.distinct() if admin.id != instance.id
            ]
            
            if notifications:
                Notification.objects.bulk_create(notifications)
        except Exception as e:
            print(f"Failed to create user registration notifications: {e}")
