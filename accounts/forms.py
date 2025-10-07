from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
import re


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    
    personal_email = forms.EmailField(required=True)
    univ_email = forms.EmailField(required=False, help_text='Optional: Must end with @cit.edu if provided')
    stud_id = forms.CharField(
        max_length=11,
        required=False,
        help_text='Optional: Format ##-####-### or ####-#### if provided'
    )
    display_name = forms.CharField(max_length=100, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'personal_email', 'univ_email', 'stud_id', 'display_name', 
                 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_univ_email(self):
        univ_email = self.cleaned_data.get('univ_email')
        if univ_email and not univ_email.endswith('@cit.edu'):
            raise ValidationError('University email must end with @cit.edu')
        return univ_email.lower() if univ_email else univ_email
    
    def clean_stud_id(self):
        stud_id = self.cleaned_data.get('stud_id')
        if stud_id:
            pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4}-\d{4}$'
            if not re.fullmatch(pattern, stud_id):
                raise ValidationError('Student ID must be in format ##-####-### or ####-####')
        return stud_id
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise ValidationError('Password must be at least 8 characters long')
            if not re.search(r'[A-Za-z]', password1):
                raise ValidationError('Password must contain at least one letter')
            if not re.search(r'\d', password1):
                raise ValidationError('Password must contain at least one number')
        return password1
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.personal_email = self.cleaned_data['personal_email']
        user.univ_email = self.cleaned_data['univ_email']
        user.stud_id = self.cleaned_data['stud_id']
        user.display_name = self.cleaned_data['display_name']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = user.personal_email  # Set Django's email field
        
        if commit:
            user.save()
        return user
    
class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form supporting student ID and university email"""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'placeholder': 'Username, Student ID, or University Email'})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Try to find user by different identifiers
        user = None
        
        # First try username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        
        # Try student ID
        if not user:
            try:
                user = User.objects.get(stud_id=username)
            except User.DoesNotExist:
                pass
        
        # Try university email
        if not user:
            try:
                user = User.objects.get(univ_email=username.lower())
            except User.DoesNotExist:
                pass
        
        if not user:
            raise ValidationError('Invalid username, student ID, or university email')
        
        if user.is_banned:
            raise ValidationError('This account has been banned')
        
        return username
    
    def get_user(self):
        """Get the user object based on the cleaned username"""
        username = self.cleaned_data.get('username')
        
        # Try different lookup methods
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        
        try:
            return User.objects.get(stud_id=username)
        except User.DoesNotExist:
            pass
        
        try:
            return User.objects.get(univ_email=username.lower())
        except User.DoesNotExist:
            pass
        
        return None
    
class PasswordChangeForm(forms.Form):
    """Custom password change form with validation"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'})
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise ValidationError('Current password is incorrect')
        return current_password
    
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            if len(new_password1) < 8:
                raise ValidationError('Password must be at least 8 characters long')
            if not re.search(r'[A-Za-z]', new_password1):
                raise ValidationError('Password must contain at least one letter')
            if not re.search(r'\d', new_password1):
                raise ValidationError('Password must contain at least one number')
        return new_password1
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('New passwords do not match')
        
        return cleaned_data
    
    def save(self):
        """Save the new password"""
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.must_change_password = False  # Clear the flag
        self.user.save()
        return self.user