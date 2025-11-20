"""
Signals for Quiz app notifications
Handles: new uploads, verification status changes, ratings, and comments
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import Quiz, QuizRating, QuizComment
from accounts.models import Notification

User = get_user_model()


@receiver(post_save, sender=Quiz)
def notify_new_quiz_upload(sender, instance, created, **kwargs):
    """
    Notify all students when a new public Quiz is uploaded.
    Notify all professors when a new Quiz needs review.
    Triggered when: A new Quiz is created and is_public=True or verification_status='pending'
    """
    if created:
        try:
            # Notify students if public
            if instance.is_public:
                # Get all users except the creator
                students = User.objects.filter(is_professor=False).exclude(id=instance.creator.id)
                
                # Create bulk notifications for students
                notifications = [
                    Notification(
                        user=student,
                        type='new_upload',
                        message=f"New Quiz uploaded: '{instance.title}' on {instance.created_at.strftime('%Y-%m-%d at %I:%M %p')}",
                        url=reverse('quizzes:quiz_detail', args=[instance.id]),
                        related_object_type='quiz',
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
                        message=f"New Quiz submitted by {instance.creator.get_display_name()} for review: '{instance.title}'",
                        url=reverse('quizzes:quiz_detail', args=[instance.id]),
                        related_object_type='quiz',
                        related_object_id=instance.id
                    )
                    for professor in professors
                ]
                if prof_notifications:
                    Notification.objects.bulk_create(prof_notifications)
        except Exception as e:
            print(f"Failed to create upload notifications for Quiz {instance.id}: {e}")


@receiver(pre_save, sender=Quiz)
def notify_quiz_verification_status_change(sender, instance, **kwargs):
    """
    Notify the creator when their Quiz verification status changes.
    Triggered when: verification_status changes from pending to verified/not_verified
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Quiz.objects.get(pk=instance.pk)
            old_status = old_instance.verification_status
            new_status = instance.verification_status
            
            # Check if status changed from pending
            if old_status == 'pending' and new_status in ['verified', 'not_verified']:
                try:
                    if new_status == 'verified':
                        message = f"Your Quiz '{instance.title}' has been accepted and is now public."
                        notif_type = 'verification_approved'
                    else:
                        message = f"Your Quiz '{instance.title}' was rejected. Please check for feedback or contact a moderator."
                        notif_type = 'verification_rejected'
                    
                    Notification.objects.create(
                        user=instance.creator,
                        type=notif_type,
                        message=message,
                        url=reverse('quizzes:quiz_detail', args=[instance.id]),
                        related_object_type='quiz',
                        related_object_id=instance.id
                    )
                except Exception as e:
                    print(f"Failed to create verification notification for Quiz {instance.id}: {e}")
        except Quiz.DoesNotExist:
            pass


@receiver(post_save, sender=QuizRating)
def notify_new_quiz_rating(sender, instance, created, **kwargs):
    """
    Notify the quiz creator when someone rates their quiz.
    Triggered when: A new QuizRating is created
    """
    if created:
        # Don't notify if user rates their own content
        if instance.user.id != instance.quiz.creator.id:
            try:
                Notification.objects.create(
                    user=instance.quiz.creator,
                    type='new_rating',
                    message=f"Someone rated your Quiz '{instance.quiz.title}'.",
                    url=reverse('quizzes:quiz_detail', args=[instance.quiz.id]),
                    related_object_type='quiz',
                    related_object_id=instance.quiz.id
                )
            except Exception as e:
                print(f"Failed to create rating notification for Quiz {instance.quiz.id}: {e}")


@receiver(post_save, sender=QuizComment)
def notify_new_quiz_comment(sender, instance, created, **kwargs):
    """
    Notify the quiz creator when someone comments on their quiz.
    Triggered when: A new QuizComment is created
    """
    if created:
        # Don't notify if user comments on their own content
        if instance.user.id != instance.quiz.creator.id:
            try:
                Notification.objects.create(
                    user=instance.quiz.creator,
                    type='new_comment',
                    message=f"Someone commented on your Quiz '{instance.quiz.title}'.",
                    url=reverse('quizzes:quiz_detail', args=[instance.quiz.id]),
                    related_object_type='quiz',
                    related_object_id=instance.quiz.id
                )
            except Exception as e:
                print(f"Failed to create comment notification for Quiz {instance.quiz.id}: {e}")
