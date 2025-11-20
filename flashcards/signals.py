"""
Signals for Flashcards app notifications
Handles: new uploads, verification status changes, ratings, and comments
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from .models import Deck, DeckRating, DeckComment
from accounts.models import Notification

User = get_user_model()


@receiver(post_save, sender=Deck)
def notify_new_deck_upload(sender, instance, created, **kwargs):
    """
    Notify all students when a new public Deck is uploaded.
    Notify all professors when a new Deck needs review.
    Triggered when: A new Deck is created and visibility='public' or verification_status='pending'
    """
    if created:
        try:
            # Notify students if public
            if instance.visibility == 'public':
                # Get all users except the owner
                students = User.objects.filter(is_professor=False).exclude(id=instance.owner.id)
                
                # Create bulk notifications for students
                notifications = [
                    Notification(
                        user=student,
                        type='new_upload',
                        message=f"New Flashcard Deck uploaded: '{instance.title}' on {instance.created_at.strftime('%Y-%m-%d at %I:%M %p')}",
                        url=reverse('flashcards:deck_detail', args=[instance.id]),
                        related_object_type='flashcard',
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
                        message=f"New Flashcard Deck submitted by {instance.owner.get_display_name()} for review: '{instance.title}'",
                        url=reverse('flashcards:deck_detail', args=[instance.id]),
                        related_object_type='flashcard',
                        related_object_id=instance.id
                    )
                    for professor in professors
                ]
                if prof_notifications:
                    Notification.objects.bulk_create(prof_notifications)
        except Exception as e:
            print(f"Failed to create upload notifications for Deck {instance.id}: {e}")


@receiver(pre_save, sender=Deck)
def notify_deck_verification_status_change(sender, instance, **kwargs):
    """
    Notify the owner when their Deck verification status changes.
    Triggered when: verification_status changes from pending to verified
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Deck.objects.get(pk=instance.pk)
            old_status = old_instance.verification_status
            new_status = instance.verification_status
            
            # Check if status changed from pending to verified
            if old_status == 'pending' and new_status == 'verified':
                try:
                    message = f"Your Flashcard Deck '{instance.title}' has been accepted and is now public."
                    
                    Notification.objects.create(
                        user=instance.owner,
                        type='verification_approved',
                        message=message,
                        url=reverse('flashcards:deck_detail', args=[instance.id]),
                        related_object_type='flashcard',
                        related_object_id=instance.id
                    )
                except Exception as e:
                    print(f"Failed to create verification notification for Deck {instance.id}: {e}")
        except Deck.DoesNotExist:
            pass


@receiver(post_save, sender=DeckRating)
def notify_new_deck_rating(sender, instance, created, **kwargs):
    """
    Notify the deck owner when someone rates their deck.
    Triggered when: A new DeckRating is created
    """
    if created:
        # Don't notify if user rates their own content
        if instance.user.id != instance.deck.owner.id:
            try:
                Notification.objects.create(
                    user=instance.deck.owner,
                    type='new_rating',
                    message=f"Someone rated your Flashcard Deck '{instance.deck.title}'.",
                    url=reverse('flashcards:deck_detail', args=[instance.deck.id]),
                    related_object_type='flashcard',
                    related_object_id=instance.deck.id
                )
            except Exception as e:
                print(f"Failed to create rating notification for Deck {instance.deck.id}: {e}")


@receiver(post_save, sender=DeckComment)
def notify_new_deck_comment(sender, instance, created, **kwargs):
    """
    Notify the deck owner when someone comments on their deck.
    Triggered when: A new DeckComment is created
    """
    if created:
        # Don't notify if user comments on their own content
        if instance.user.id != instance.deck.owner.id:
            try:
                Notification.objects.create(
                    user=instance.deck.owner,
                    type='new_comment',
                    message=f"Someone commented on your Flashcard Deck '{instance.deck.title}'.",
                    url=reverse('flashcards:deck_detail', args=[instance.deck.id]),
                    related_object_type='flashcard',
                    related_object_id=instance.deck.id
                )
            except Exception as e:
                print(f"Failed to create comment notification for Deck {instance.deck.id}: {e}")
