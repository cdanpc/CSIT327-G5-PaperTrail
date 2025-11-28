"""
Test password reset email to verify the correct domain is used
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.forms import CITPasswordResetForm
from django.conf import settings

User = get_user_model()

print("\n" + "="*70)
print("PASSWORD RESET EMAIL TEST")
print("="*70)

print(f"\n📧 Current Configuration:")
print(f"   SITE_DOMAIN: {settings.SITE_DOMAIN}")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   Protocol: {'http' if settings.DEBUG else 'https'}")
print(f"   Full URL: {'http' if settings.DEBUG else 'https'}://{settings.SITE_DOMAIN}")

# Test with a sample email
test_email = input("\n📝 Enter a Gmail address to test (must exist in database): ")

if test_email:
    form = CITPasswordResetForm({'email': test_email})
    
    if form.is_valid():
        print(f"\n✅ Form is valid. Sending password reset email to: {test_email}")
        form.save(
            request=None,
            use_https=not settings.DEBUG,
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
        )
        print(f"\n📬 Email sent successfully!")
        print(f"\n✨ The email will contain a clickable link to:")
        print(f"   {'http' if settings.DEBUG else 'https'}://{settings.SITE_DOMAIN}/reset/<token>/")
        print("\n💡 Check your Gmail inbox (including spam folder)")
    else:
        print(f"\n❌ Form errors: {form.errors}")
        
print("\n" + "="*70)
