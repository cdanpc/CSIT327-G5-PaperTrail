from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import re


class User(AbstractUser):
    """Custom User model extending AbstractUser"""
    
    # Additional fields beyond the default AbstractUser fields
    display_name = models.CharField(max_length=100, blank=False)
    stud_id = models.CharField(
        max_length=11, 
        blank=True, 
        null=True,
        unique=True,
        help_text='Format: ##-####-### or ####-####'
    )
    personal_email = models.EmailField(blank=False, unique=True)
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
    
    # Role flags
    is_professor = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Validate university email
        if self.univ_email and not self.univ_email.endswith('@cit.edu'):
            raise ValidationError({'univ_email': 'University email must end with @cit.edu'})
        
        # Validate student ID format
        if self.stud_id:
            pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4}-\d{4})$'
            if not re.fullmatch(pattern, self.stud_id):
                raise ValidationError({'stud_id': 'Student ID must be in format ##-####-### or ####-####'})
    
    def get_display_name(self):
        """Return the display name or username if display_name is empty"""
        return self.display_name if self.display_name else self.username
    
    def get_role(self):
        """Get user's primary role"""
        if self.is_superuser or self.is_staff:
            return 'admin'
        elif self.is_professor:
            return 'professor'
        else:
            return 'student'
    
    def get_dashboard_url(self):
        """Return appropriate dashboard URL based on role"""
        role = self.get_role()
        from django.urls import reverse
        
        if role == 'admin':
            return reverse('accounts:admin_dashboard')
        elif role == 'professor':
            return reverse('accounts:professor_dashboard')
        else:
            return reverse('accounts:student_dashboard')
    
    def save(self, *args, **kwargs):
        """Override save to handle email and lowercase conversions"""
        if self.univ_email:
            self.univ_email = self.univ_email.lower()
        if self.personal_email:
            self.personal_email = self.personal_email.lower()
            # Set Django's email field to personal_email
            self.email = self.personal_email
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.get_display_name()} ({self.username})"