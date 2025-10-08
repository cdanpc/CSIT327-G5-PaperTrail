from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User
import re


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='First Name',
        help_text='Enter your given name',
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
        help_text='Enter your family name',
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
        help_text='This is how others will see your name.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a display name',
            'data-display-name-target': 'true'
        })
    )
    personal_email = forms.EmailField(
        required=True,
        label='Personal Email',
        help_text='Format: Must end with @gmail.com)',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'your.name@gmail.com'
        })
    )
    univ_email = forms.EmailField(
        required=False,
        label='University Email',
        help_text='Format: Must end with @cit.edu)',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'student.id@cit.edu'
        })
    )
    stud_id = forms.CharField(
        max_length=11,
        required=False,
        label='Student ID',
        help_text='Format: ##-####-### (e.g., 20-1234-567)',
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
    """Custom login form supporting student ID and university email"""
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'Username, Student ID, or University Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Try to find user by different identifiers
            user = None
            
            # Try username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass
            
            # Try student ID
            if not user and username:
                try:
                    user = User.objects.get(stud_id=username)
                except User.DoesNotExist:
                    pass
            
            # Try university email
            if not user and username:
                try:
                    user = User.objects.get(univ_email=username.lower())
                except User.DoesNotExist:
                    pass
            
            if user:
                if user.is_banned:
                    raise ValidationError('This account has been banned')
                
                # Set username for authentication
                self.cleaned_data['username'] = user.username
                
                # Call parent's clean to handle authentication
                super().clean()
            else:
                raise ValidationError('Invalid username, student ID, or university email')
        
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
            pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4}-\d{4})$'
            if not re.fullmatch(pattern, stud_id):
                raise ValidationError('Student ID must be in format ##-####-###')
        return stud_id


class CustomPasswordChangeForm(DjangoPasswordChangeForm):
    """Custom password change form with validation"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )
    
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
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'must_change_password'):
            user.must_change_password = False
            if commit:
                user.save()
        return user