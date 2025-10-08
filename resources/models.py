from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Resource(models.Model):
    """Resources uploaded by users"""
    
    RESOURCE_TYPES = [
        ('pdf', 'PDF Document'),
        ('ppt', 'PowerPoint Presentation'),
        ('pptx', 'PowerPoint Presentation (PPTX)'),
        ('docx', 'Word Document'),
        ('txt', 'Text Document'),
        ('image', 'Image'),
        ('link', 'External Link'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('not_verified', 'Not Verified'),
    ]


    
    # Basic info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_resources')
    
    # Resource type and content
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    file_url = models.URLField(blank=True, null=True, help_text='URL to uploaded file in Supabase Storage')
    external_url = models.URLField(blank=True, null=True, help_text='External link URL')
    original_filename = models.CharField(max_length=255, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text='File size in bytes')
    
    # Metadata
    tags = models.ManyToManyField(Tag, blank=True, related_name='resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Approval and verification
    approved = models.BooleanField(default=False)
    flagged_for_verification = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=15, 
        choices=VERIFICATION_STATUS, 
        default='pending'
    )
    verification_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_resources'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    views_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    
    def clean(self):
        """Validate that either file_url or external_url is provided, but not both"""
        # Handle N/A values in external_url
        if self.external_url and str(self.external_url).lower().strip() in ['n/a', 'na', 'none', '']:
            self.external_url = None
        
        # Skip validation during form validation - let the form handle it
        if hasattr(self, '_state') and self._state.adding:
            return
        
        if not self.file_url and not self.external_url:
            raise ValidationError('Either file upload or external URL must be provided')
        
        if self.file_url and self.external_url:
            # Prefer file upload, ignore external URL
            self.external_url = None
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_verification_badge(self):
        """Return verification status badge"""
        if self.verification_status == 'verified':
            return 'verified'
        elif self.verification_status == 'not_verified':
            return 'not-verified'
        return 'pending'
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Bookmark(models.Model):
    """User bookmarks for resources"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'resource']
        ordering = ['-created_at']