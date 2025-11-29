"""
Signals for Resource app notifications
Handles: new uploads, verification status changes, ratings, and comments
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import Resource, Rating, Comment
from accounts.models import Notification

User = get_user_model()


@receiver(post_save, sender=Resource)
def notify_new_resource_upload(sender, instance, created, **kwargs):
    """
    Notify all students when a new public Resource is uploaded.
    Notify all professors when a new Resource needs review.
    Triggered when: A new Resource is created and is_public=True or verification_status='pending'
    """
    if created:
        try:
            # Notify students if public
            if instance.is_public:
                # Get all users except the uploader
                students = User.objects.filter(is_professor=False).exclude(id=instance.uploader.id)
                
                # Create bulk notifications for students
                notifications = [
                    Notification(
                        user=student,
                        type='new_upload',
                        message=f"New Resource uploaded: '{instance.title}' on {instance.created_at.strftime('%Y-%m-%d at %I:%M %p')}",
                        url=reverse('resources:resource_detail', args=[instance.id]),
                        related_object_type='resource',
                        related_object_id=instance.id
                    )
                    for student in students
                ]
                Notification.objects.bulk_create(notifications)
            
            # Notify professors if pending review
            if instance.verification_status == 'pending':
                professors = User.objects.filter(is_professor=True)
                
                # Create bulk notifications for professors
                prof_notifications = [
                    Notification(
                        user=professor,
                        type='content_review',
                        message=f"New Resource submitted by {instance.uploader.get_display_name()} for review: '{instance.title}'",
                        url=reverse('resources:resource_detail', args=[instance.id]),
                        related_object_type='resource',
                        related_object_id=instance.id
                    )
                    for professor in professors
                ]
                if prof_notifications:
                    Notification.objects.bulk_create(prof_notifications)
        except Exception as e:
            print(f"Failed to create upload notifications for Resource {instance.id}: {e}")


@receiver(pre_save, sender=Resource)
def notify_verification_status_change(sender, instance, **kwargs):
    """
    Notify the uploader when their Resource verification status changes.
    Triggered when: verification_status changes from pending to verified/not_verified
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Resource.objects.get(pk=instance.pk)
            old_status = old_instance.verification_status
            new_status = instance.verification_status
            
            # Check if status changed from pending
            if old_status == 'pending' and new_status in ['verified', 'not_verified']:
                try:
                    if new_status == 'verified':
                        message = f"Your Resource '{instance.title}' has been accepted and is now public."
                        notif_type = 'verification_approved'
                    else:
                        message = f"Your Resource '{instance.title}' was rejected. Please check for feedback or contact a moderator."
                        notif_type = 'verification_rejected'
                    
                    Notification.objects.create(
                        user=instance.uploader,
                        type=notif_type,
                        message=message,
                        url=reverse('resources:resource_detail', args=[instance.id]),
                        related_object_type='resource',
                        related_object_id=instance.id
                    )
                except Exception as e:
                    print(f"Failed to create verification notification for Resource {instance.id}: {e}")
        except Resource.DoesNotExist:
            pass


@receiver(post_save, sender=Rating)
def notify_new_rating(sender, instance, created, **kwargs):
    """
    Notify the resource uploader when someone rates their resource.
    Triggered when: A new Rating is created
    """
    if created:
        # Don't notify if user rates their own content
        if instance.user.id != instance.resource.uploader.id:
            try:
                Notification.objects.create(
                    user=instance.resource.uploader,
                    type='new_rating',
                    message=f"Someone rated your Resource '{instance.resource.title}'.",
                    url=reverse('resources:resource_detail', args=[instance.resource.id]),
                    related_object_type='resource',
                    related_object_id=instance.resource.id
                )
            except Exception as e:
                print(f"Failed to create rating notification for Resource {instance.resource.id}: {e}")


@receiver(post_save, sender=Comment)
def notify_new_comment(sender, instance, created, **kwargs):
    """
    Notify the resource uploader when someone comments on their resource.
    Triggered when: A new Comment is created
    """
    if created:
        # Don't notify if user comments on their own content
        if instance.user.id != instance.resource.uploader.id:
            try:
                Notification.objects.create(
                    user=instance.resource.uploader,
                    type='new_comment',
                    message=f"Someone commented on your Resource '{instance.resource.title}'.",
                    url=reverse('resources:resource_detail', args=[instance.resource.id]),
                    related_object_type='resource',
                    related_object_id=instance.resource.id
                )
            except Exception as e:
                print(f"Failed to create comment notification for Resource {instance.resource.id}: {e}")
