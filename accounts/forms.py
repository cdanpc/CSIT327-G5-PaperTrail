from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User
import re


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='First Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'data-display-name-source': 'true'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Last Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'data-display-name-source': 'true'
        })
    )
    display_name = forms.CharField(
        max_length=100,
        required=True,
        label='Display Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a display name',
            'data-display-name-target': 'true'
        })
    )
    personal_email = forms.EmailField(
        required=True,
        label='Personal Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'your.name@gmail.com'
        })
    )
    univ_email = forms.EmailField(
        required=True,
        label='University Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'student.id@cit.edu'
        })
    )
    stud_id = forms.CharField(
        max_length=11,
        required=True,
        label='Student ID',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Example: 20-1234-567'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'personal_email', 'univ_email', 'stud_id', 'display_name', 
                 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        
        # Remove Django's default password help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
    
    def clean_univ_email(self):
        univ_email = self.cleaned_data.get('univ_email')
        if univ_email and not univ_email.endswith('@cit.edu'):
            raise ValidationError('University email must end with @cit.edu')
        return univ_email.lower() if univ_email else univ_email
    
    def clean_stud_id(self):
        stud_id = self.cleaned_data.get('stud_id')
        if stud_id:
            pattern = r'^\d{2}-\d{4}-\d{3}$'
            if not re.fullmatch(pattern, stud_id):
                raise ValidationError('Student ID must be in format ##-####-###')
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
        user.univ_email = self.cleaned_data.get('univ_email') or None
        user.stud_id = self.cleaned_data.get('stud_id') or None
        user.display_name = self.cleaned_data['display_name']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form supporting username, student ID, and university email"""

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that they are case-sensitive."
        ),
        'inactive': _("This account is inactive."),
        'banned': _("This account has been banned. Please contact support."),
    }
    
    username = forms.CharField(
        max_length=254,
        label='',
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Username, Student ID, or University Email'
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        username_input = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username_input and password:
            # Try to find user by different identifiers
            user = None
            identifier_type = None
            
            # Check if input matches student ID format (supports both formats: ##-####-### or ####)
            stud_id_pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4})$'
            if re.fullmatch(stud_id_pattern, username_input):
                identifier_type = 'student_id'
                try:
                    user = User.objects.get(stud_id=username_input)
                except User.DoesNotExist:
                    raise ValidationError(
                        'Student ID not found. This Student ID is not registered in the system. Please check your Student ID or register for a new account.',
                        code='invalid_student_id'
                    )
            
            # Check if input looks like an email (contains @)
            elif '@' in username_input:
                identifier_type = 'email'
                # Check if it's a university email
                if username_input.lower().endswith('@cit.edu'):
                    try:
                        user = User.objects.get(univ_email=username_input.lower())
                    except User.DoesNotExist:
                        raise ValidationError(
                            'University Email not found. This email is not registered in the system. Please check your email or register for a new account.',
                            code='invalid_email'
                        )
                else:
                    raise ValidationError(
                        'Invalid University Email. University email must end with @cit.edu',
                        code='invalid_email_format'
                    )
            
            # Otherwise, treat as username
            else:
                identifier_type = 'username'
                try:
                    user = User.objects.get(username=username_input)
                except User.DoesNotExist:
                    raise ValidationError(
                        'Username not found. This username is not registered in the system. Please check your username or register for a new account.',
                        code='invalid_username'
                    )
            
            # If user found, check if banned
            if user and user.is_banned:
                raise ValidationError(
                    'This account has been banned. Please contact support.',
                    code='banned'
                )
            
            # If user found, verify password
            if user:
                # Check if password is correct
                if not user.check_password(password):
                    raise ValidationError(
                        'Invalid Password. Please check your password and try again. Note that passwords are case-sensitive.',
                        code='invalid_password'
                    )
                
                # Check if user is active
                if not user.is_active:
                    raise ValidationError(
                        self.error_messages['inactive'],
                        code='inactive'
                    )
                
                # Set the actual username for Django's authentication
                self.user_cache = user
                self.cleaned_data['username'] = user.username
        
        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['display_name', 'first_name', 'last_name', 'personal_email', 
                 'univ_email', 'stud_id', 'profile_picture']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'univ_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'stud_id': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_univ_email(self):
        univ_email = self.cleaned_data.get('univ_email')
        if univ_email and not univ_email.endswith('@cit.edu'):
            raise ValidationError('University email must end with @cit.edu')
        return univ_email.lower() if univ_email else univ_email
    
    def clean_stud_id(self):
        stud_id = self.cleaned_data.get('stud_id')
        if stud_id:
            pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4})$'
            if not re.fullmatch(pattern, stud_id):
                raise ValidationError('Student ID must be in format ##-####-### (students) or #### (professors)')
        return stud_id


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    """Custom password change form with enhanced validation and specific error messages"""
    
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter current password'})
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'})
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Re-enter new password'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override error messages for old password
        self.fields['old_password'].error_messages = {
            'required': 'Please enter your current password.',
        }
        self.fields['new_password1'].error_messages = {
            'required': 'Please enter a new password.',
        }
        self.fields['new_password2'].error_messages = {
            'required': 'Please confirm your new password.',
        }
    
    def clean_old_password(self):
        """Validate the old password with specific error message"""
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError(
                'Your current password is incorrect. Please try again.',
                code='password_incorrect'
            )
        return old_password
    
    def clean_new_password1(self):
        """Validate new password strength"""
        new_password1 = self.cleaned_data.get('new_password1')
        old_password = self.data.get('old_password')
        
        if new_password1:
            # Check length
            if len(new_password1) < 8:
                raise ValidationError(
                    'Password must be at least 8 characters long.',
                    code='password_too_short'
                )
            
            # Check for letters
            if not re.search(r'[A-Za-z]', new_password1):
                raise ValidationError(
                    'Password must contain at least one letter (A-Z or a-z).',
                    code='password_no_letters'
                )
            
            # Check for numbers
            if not re.search(r'\d', new_password1):
                raise ValidationError(
                    'Password must contain at least one number (0-9).',
                    code='password_no_numbers'
                )
            
            # Check if new password is same as old password
            if old_password and new_password1 == old_password:
                raise ValidationError(
                    'Your new password cannot be the same as your current password.',
                    code='password_same_as_old'
                )
        
        return new_password1
    
    def clean_new_password2(self):
        """Validate password confirmation"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(
                    'The two password fields do not match. Please make sure you enter the same password twice.',
                    code='password_mismatch'
                )
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'must_change_password'):
            user.must_change_password = False
            if commit:
                user.save()
        return user