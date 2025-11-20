from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from .models import User
import re


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='First Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Last Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doe'})
    )
    personal_email = forms.EmailField(
        required=True,
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
    )
    univ_email = forms.EmailField(
        required=True,
        label='University Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student.id@cit.edu'})
    )
    stud_id = forms.CharField(
        max_length=11,
        required=True,
        label='Student ID',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '20-1234-567'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'personal_email', 'univ_email', 'stud_id', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '********'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '********'})
        self.fields['password1'].help_text = 'At least 8 characters.'

    def clean_univ_email(self):
        univ_email = self.cleaned_data.get('univ_email')
        if univ_email and not univ_email.endswith('@cit.edu'):
            raise ValidationError('University email must end with @cit.edu')
        return univ_email.lower() if univ_email else univ_email

    def clean_stud_id(self):
        stud_id = self.cleaned_data.get('stud_id')
        if stud_id and not re.fullmatch(r'^\d{2}-\d{4}-\d{3}$', stud_id):
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
        # Store both stud_id and univ_email separately (both required during registration)
        user.stud_id = self.cleaned_data['stud_id']  # Store Student ID in its own field
        user.univ_email = self.cleaned_data['univ_email']  # Store University Email in its own field
        
        # Use Student ID as username for Django's authentication system
        user.username = self.cleaned_data['stud_id']
        
        # Store other required fields
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.personal_email = self.cleaned_data['personal_email']
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login that accepts Student ID or University Email plus password."""

    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that they are case-sensitive."
        ),
        'inactive': _("This account is inactive."),
        'banned': _("This account has been banned. Please contact support."),
    }

    username = forms.CharField(
        max_length=254,
        label='Email or Student ID',
        widget=forms.TextInput(attrs={
            'autofocus': True,
            'class': 'form-control',
            'placeholder': 'student@cit.edu or 20-1234-567'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '********'})
    )

    def clean(self):
        username_input = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username_input and password:
            user = None
            stud_id_pattern = r'^(?:\d{2}-\d{4}-\d{3}|\d{4})$'
            try:
                if re.fullmatch(stud_id_pattern, username_input):
                    try:
                        user = User.objects.get(stud_id=username_input)
                    except User.DoesNotExist:
                        user = None
                elif '@' in username_input and username_input.lower().endswith('@cit.edu'):
                    try:
                        user = User.objects.get(univ_email=username_input.lower())
                    except User.DoesNotExist:
                        user = None
            except Exception as e:
                # Catch any database errors
                raise ValidationError(
                    'An error occurred while processing your login. Please try again.',
                    code='database_error'
                )
            
            if not user:
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': 'Student ID or University Email'},
                )
            if user.is_banned:
                raise ValidationError(self.error_messages['banned'], code='banned')
            if not user.check_password(password):
                raise ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': 'Student ID or University Email'},
                )
            if not user.is_active:
                raise ValidationError(self.error_messages['inactive'], code='inactive')
            self.user_cache = user
        return self.cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'personal_email', 'univ_email', 
            'stud_id', 'profile_picture', 'tagline', 'bio', 
            'department', 'year_level', 'phone'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'personal_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'univ_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'stud_id': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'tagline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Computer Science Student | Active Contributor',
                'maxlength': '100'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'maxlength': '500'
            }),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'year_level': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'Select year'),
                ('1', '1st Year'),
                ('2', '2nd Year'),
                ('3', '3rd Year'),
                ('4', '4th Year'),
            ]),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
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

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if new_password1:
            if len(new_password1) < 8:
                raise ValidationError('Password must be at least 8 characters long.', code='password_too_short')
            if not re.search(r'[A-Za-z]', new_password1):
                raise ValidationError('Password must contain at least one letter (A-Z or a-z).', code='password_no_letters')
            if not re.search(r'\d', new_password1):
                raise ValidationError('Password must contain at least one number (0-9).', code='password_no_numbers')
        return new_password1


class ForgotPasswordRequestForm(forms.Form):
    """Form for requesting a password reset via email"""
    
    email = forms.EmailField(
        label='Email Address',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email (Gmail or @cit.edu)',
            'autofocus': True
        }),
        help_text='Enter the email address associated with your account'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            # Check if email is gmail or cit.edu
            if not (email.endswith('@gmail.com') or email.endswith('@cit.edu')):
                raise ValidationError('Please use a Gmail or CIT University email address.')
            
            # Check if user exists with this email
            user = User.objects.filter(
                Q(personal_email=email) | Q(univ_email=email)
            ).first()
            
            if not user:
                raise ValidationError('No account found with this email address.')
            
            self.user = user  # Store user for later use
        return email


class VerifyCodeForm(forms.Form):
    """Form for verifying the 6-character reset code"""
    
    code = forms.CharField(
        label='Verification Code',
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center text-uppercase',
            'placeholder': 'Enter 6-character code',
            'maxlength': '6',
            'style': 'letter-spacing: 0.5em; font-size: 1.5rem; font-weight: bold;',
            'autofocus': True
        }),
        help_text='Enter the 6-character code sent to your email'
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper().strip()
            # Validate format (6 alphanumeric characters)
            if not re.fullmatch(r'^[A-Z0-9]{6}$', code):
                raise ValidationError('Code must be 6 characters (letters and numbers only).')
        return code


class ResetPasswordForm(forms.Form):
    """Form for setting a new password after verification"""
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autofocus': True
        }),
        help_text='Must be at least 8 characters with letters and numbers'
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter new password'
        })
    )
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            if not re.search(r'[A-Za-z]', password):
                raise ValidationError('Password must contain at least one letter.')
            if not re.search(r'\d', password):
                raise ValidationError('Password must contain at least one number.')
            if not re.search(r'[A-Z]', password):
                raise ValidationError('Password must contain at least one uppercase letter.')
            if not re.search(r'[a-z]', password):
                raise ValidationError('Password must contain at least one lowercase letter.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('The two password fields must match.')
        
        return cleaned_data


class ChangePersonalEmailForm(forms.Form):
    """Form for changing personal email address"""
    
    new_email = forms.EmailField(
        label='New Personal Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
            'autofocus': True
        }),
        help_text='Enter your new personal email address'
    )
    confirm_email = forms.EmailField(
        label='Confirm Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new email'
        })
    )
    password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        }),
        help_text='For security, please enter your current password'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if new_email:
            new_email = new_email.lower().strip()
            
            # Check if email is already in use
            if User.objects.filter(personal_email=new_email).exclude(id=self.user.id).exists():
                raise ValidationError('This email is already in use by another account.')
            
            # Check if it's the same as current email
            if new_email == self.user.personal_email:
                raise ValidationError('This is already your current email address.')
        
        return new_email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not self.user.check_password(password):
            raise ValidationError('Incorrect password. Please try again.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        confirm_email = cleaned_data.get('confirm_email')
        
        if new_email and confirm_email and new_email != confirm_email:
            raise ValidationError('Email addresses do not match.')
        
        return cleaned_data


class CITPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form that accepts Gmail only (@gmail.com)
    for password resets using Gmail SMTP
    """
    email = forms.EmailField(
        label='Gmail Address',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@gmail.com',
            'autofocus': True
        }),
        help_text='Enter your Gmail address associated with your account'
    )
    
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Override to use the correct domain from settings instead of localhost
        """
        from django.conf import settings
        
        # Determine protocol based on DEBUG mode
        context['protocol'] = 'http' if settings.DEBUG else 'https'
        context['domain'] = settings.SITE_DOMAIN
        
        super().send_mail(
            subject_template_name, email_template_name, context, from_email,
            to_email, html_email_template_name
        )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower().strip()
            
            # Accept Gmail only
            if not email.endswith('@gmail.com'):
                raise ValidationError(
                    'Please use your Gmail address (@gmail.com).',
                    code='invalid_domain'
                )
            
            # Check if a user exists with this Gmail
            user_exists = User.objects.filter(
                personal_email__iexact=email
            ).exists()
            
            if not user_exists:
                # For security, we still show success message but don't reveal if email exists
                # The form will handle this in get_users()
                pass
        
        return email
    
    def get_users(self, email):
        """
        Override to query by personal_email field only (Gmail)
        """
        active_users = User.objects.filter(
            personal_email__iexact=email,
            is_active=True
        )
        return (u for u in active_users)


class CITSetPasswordForm(SetPasswordForm):
    """
    Custom set password form with enhanced styling and validation
    """
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autofocus': True
        }),
        help_text='Must be at least 8 characters with letters and numbers'
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter new password'
        })
    )
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            if len(password) < 8:
                raise ValidationError('Password must be at least 8 characters long.')
            if not re.search(r'[A-Za-z]', password):
                raise ValidationError('Password must contain at least one letter.')
            if not re.search(r'\d', password):
                raise ValidationError('Password must contain at least one number.')
        return password


class ChangeUniversityEmailForm(forms.Form):
    """Form for changing university email address (requires admin verification)"""
    
    new_univ_email = forms.EmailField(
        label='New University Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'student.id@cit.edu',
            'autofocus': True
        }),
        help_text='Enter your new CIT university email address'
    )
    confirm_univ_email = forms.EmailField(
        label='Confirm University Email',
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new university email'
        })
    )
    password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        }),
        help_text='For security, please enter your current password'
    )
    reason = forms.CharField(
        label='Reason for Change',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please explain why you need to change your university email'
        }),
        help_text='This will be reviewed by administrators'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_univ_email(self):
        new_univ_email = self.cleaned_data.get('new_univ_email')
        if new_univ_email:
            new_univ_email = new_univ_email.lower().strip()
            
            # Must be @cit.edu
            if not new_univ_email.endswith('@cit.edu'):
                raise ValidationError('University email must end with @cit.edu')
            
            # Check if email is already in use
            if User.objects.filter(univ_email=new_univ_email).exclude(id=self.user.id).exists():
                raise ValidationError('This university email is already in use by another account.')
            
            # Check if it's the same as current email
            if new_univ_email == self.user.univ_email:
                raise ValidationError('This is already your current university email.')
        
        return new_univ_email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and not self.user.check_password(password):
            raise ValidationError('Incorrect password. Please try again.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        new_univ_email = cleaned_data.get('new_univ_email')
        confirm_univ_email = cleaned_data.get('confirm_univ_email')
        
        if new_univ_email and confirm_univ_email and new_univ_email != confirm_univ_email:
            raise ValidationError('University email addresses do not match.')
        
        return cleaned_data