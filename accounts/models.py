from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
import re
import random
import string
from datetime import timedelta


class User(AbstractUser):
    """Custom User model extending AbstractUser with academic fields."""

    # Academic identifiers
    stud_id = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        unique=True,
        help_text='Format: ##-####-### (students) or #### (professors)'
    )
    personal_email = models.EmailField(blank=True, null=True, unique=True)
    univ_email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        help_text='University email must end with @cit.edu'
    )

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        help_text='Profile picture'
    )

    # Profile Enhancement Fields (Phase 2)
    tagline = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Short tagline or bio headline (e.g., "Computer Science Student | Active Contributor")'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text='About me section'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Academic department'
    )
    year_level = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Year level (1, 2, 3, 4, etc.)'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )

    # Role flags
    is_professor = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)

    # Preferences (Phase 3)
    DASHBOARD_CHOICES = [
        ('student', 'Student Dashboard'),
        ('overview', 'Overview'),
        ('resources', 'Resources'),
        ('flashcards', 'Flashcards'),
        ('quizzes', 'Quizzes'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Español'),
        ('fr', 'Français'),
        ('tl', 'Tagalog'),
    ]
    
    default_dashboard = models.CharField(
        max_length=20,
        choices=DASHBOARD_CHOICES,
        default='student',
        help_text='Default dashboard view on login'
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text='Preferred language'
    )
    
    # Notification Preferences (Phase 4)
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications for updates'
    )
    notify_resource_downloads = models.BooleanField(
        default=True,
        help_text='Notify when your resources are downloaded'
    )
    notify_quiz_submissions = models.BooleanField(
        default=True,
        help_text='Notify about quiz submissions and results'
    )
    notify_system_updates = models.BooleanField(
        default=True,
        help_text='Receive system updates and announcements'
    )
    notify_weekly_summary = models.BooleanField(
        default=False,
        help_text='Receive weekly activity summary email'
    )
    in_app_sound = models.BooleanField(
        default=True,
        help_text='Enable notification sounds'
    )
    
    # Privacy Settings (Phase 5)
    VISIBILITY_CHOICES = [
        ('public', 'Public - Anyone can view your profile'),
        ('students_only', 'Students Only - Only CIT students can view'),
        ('private', 'Private - Only you can view your profile'),
    ]
    
    profile_visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='students_only',
        help_text='Control who can view your profile'
    )
    
    # Account Deletion (Phase 5.6)
    deletion_requested = models.BooleanField(
        default=False,
        help_text='User has requested account deletion'
    )
    deletion_requested_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When account deletion was requested'
    )
    deletion_scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When account will be permanently deleted'
    )

    # Keep default username authentication internally
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['personal_email', 'first_name', 'last_name']

    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def clean(self):
        super().clean()
        # Validate university email
        if self.univ_email and not self.univ_email.endswith('@cit.edu'):
            raise ValidationError({'univ_email': 'University email must end with @cit.edu'})
        # Validate stud_id format
        if self.stud_id:
            pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4})$'
            if not re.fullmatch(pattern, self.stud_id):
                raise ValidationError({'stud_id': 'Student ID must be in format ##-####-### (students) or #### (professors)'})

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name

    def get_short_name(self):
        return self.first_name

    def get_display_name(self):
        return self.get_full_name() or self.username

    def get_role(self):
        if self.is_superuser or self.is_staff:
            return 'admin'
        elif self.is_professor:
            return 'professor'
        else:
            return 'student'

    def get_dashboard_url(self):
        role = self.get_role()
        if role == 'admin':
            return reverse('accounts:admin_dashboard')
        elif role == 'professor':
            return reverse('accounts:professor_dashboard')
        else:
            return reverse('accounts:student_dashboard')

    def save(self, *args, **kwargs):
        # Normalize emails and sync Django's email field from personal_email
        if self.univ_email:
            self.univ_email = self.univ_email.lower()
        if self.personal_email:
            self.personal_email = self.personal_email.lower()
            self.email = self.personal_email
        else:
            # Clear email field if personal_email is not set
            self.email = ''
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    # Profile Completion Methods (Phase 7)
    def check_profile_completion(self):
        """
        Check if profile is 100% complete.
        Required fields: profile_picture, first_name, last_name, personal_email, phone, univ_email, bio
        """
        required_fields = [
            bool(self.profile_picture),
            bool(self.first_name and self.last_name and self.personal_email and self.phone),
            bool(self.univ_email),
            bool(self.bio),
        ]
        return all(required_fields)
    
    def get_profile_completion_percentage(self):
        """Calculate profile completion percentage (0-100)"""
        completed = 0
        total = 4
        
        # Photo check
        if self.profile_picture:
            completed += 1
        
        # Personal info check (firstName, lastName, personalEmail, phone)
        if self.first_name and self.last_name and self.personal_email and self.phone:
            completed += 1
        
        # University email check
        if self.univ_email:
            completed += 1
        
        # Bio check
        if self.bio:
            completed += 1
        
        return (completed / total) * 100
    
    def unlock_verified_student_badge(self):
        """
        Unlock the Verified Student badge when profile is 100% complete.
        Creates the badge if it doesn't exist.
        Returns: Achievement object or None
        """
        if not self.check_profile_completion():
            return None
        
        # Check if already unlocked
        existing = Achievement.objects.filter(
            user=self,
            achievement_type='verified_student'
        ).first()
        
        if existing:
            return existing
        
        # Get or create the Verified Student badge
        badge, created = Badge.objects.get_or_create(
            name='Verified Student',
            defaults={
                'description': 'Completed 100% of profile information',
                'icon': 'fa-certificate',
                'color': 'green',
                'requirement': 'Complete all profile sections',
                'is_active': True,
            }
        )
        
        # Create the achievement
        achievement = Achievement.objects.create(
            user=self,
            achievement_type='verified_student',
            badge=badge,
            is_displayed=True
        )
        
        return achievement


class PasswordResetToken(models.Model):
    """Model to store password reset tokens"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    email = models.EmailField(help_text='Email where the link was sent')
    token = models.CharField(max_length=100, unique=True, help_text='Unique reset token', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Token expires 1 hour after creation')
    is_used = models.BooleanField(default=False, help_text='Whether the token has been used')
    
    class Meta:
        db_table = 'accounts_password_reset_token'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Generate token if not set
        if not self.token:
            self.token = self.generate_token()
        # Set expiry to 1 hour from creation
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    
    def is_valid(self):
        """Check if the token is still valid (not expired and not used)"""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """Mark the token as used"""
        self.is_used = True
        self.save()
    
    def __str__(self):
        return f"Reset token for {self.user.get_display_name()} ({'Used' if self.is_used else 'Active' if self.is_valid() else 'Expired'})"


class Badge(models.Model):
    """Model for profile badges"""
    
    BADGE_COLORS = [
        ('purple', 'Purple'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('blue', 'Blue'),
        ('green', 'Green'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='Font Awesome icon class (e.g., fa-trophy)')
    color = models.CharField(max_length=20, choices=BADGE_COLORS, default='purple')
    requirement = models.CharField(max_length=200, help_text='How to unlock this badge')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'accounts_badge'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Achievement(models.Model):
    """Model to track user achievements"""
    
    ACHIEVEMENT_TYPES = [
        ('profile_complete', 'Profile Completed'),
        ('first_upload', 'First Upload'),
        ('helpful_contributor', 'Helpful Contributor'),
        ('quiz_creator', 'Quiz Creator'),
        ('streak_master', 'Streak Master'),
        ('top_sharer', 'Top Sharer'),
        ('verified_student', 'Verified Student'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES)
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True, related_name='achievements')
    unlocked_date = models.DateTimeField(auto_now_add=True)
    is_displayed = models.BooleanField(default=True, help_text='Show on profile')
    
    class Meta:
        db_table = 'accounts_achievement'
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        ordering = ['-unlocked_date']
        unique_together = ['user', 'achievement_type']
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.get_achievement_type_display()}"


class UserSession(models.Model):
    """Model to track active user sessions across devices"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True, help_text='Django session key')
    
    # Device information
    device_name = models.CharField(max_length=200, blank=True, help_text='Device name (e.g., Chrome on Windows)')
    device_type = models.CharField(max_length=50, blank=True, help_text='mobile, tablet, desktop')
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    
    # Location information
    ip_address = models.GenericIPAddressField(help_text='IP address of the device')
    location = models.CharField(max_length=200, blank=True, help_text='City, Country')
    
    # Session tracking
    created_at = models.DateTimeField(auto_now_add=True, help_text='First login time')
    last_activity = models.DateTimeField(auto_now=True, help_text='Last activity time')
    is_current = models.BooleanField(default=False, help_text='Current active session')
    
    class Meta:
        db_table = 'accounts_usersession'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.device_name} ({self.ip_address})"
    
    def is_active(self):
        """Check if session is still active (within last 30 minutes)"""
        from datetime import timedelta
        return self.last_activity >= timezone.now() - timedelta(minutes=30)
    
    def get_device_icon(self):
        """Return Font Awesome icon class based on device type"""
        icons = {
            'mobile': 'fa-mobile-alt',
            'tablet': 'fa-tablet-alt',
            'desktop': 'fa-desktop',
        }
        return icons.get(self.device_type, 'fa-laptop')
    
    def get_time_since_activity(self):
        """Get human-readable time since last activity"""
        from django.utils.timesince import timesince
        return timesince(self.last_activity)