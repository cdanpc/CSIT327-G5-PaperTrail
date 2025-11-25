"""
Test Gmail SMTP Configuration and Password Reset Email Sending
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User

print("=" * 80)
print("GMAIL SMTP & PASSWORD RESET EMAIL TEST")
print("=" * 80)

# Test 1: Check email settings
print("\n[STEP 1] EMAIL CONFIGURATION")
print("-" * 40)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)} (length: {len(settings.EMAIL_HOST_PASSWORD)})")
print(f"SITE_DOMAIN: {settings.SITE_DOMAIN}")

# Test 2: Try to send a test email
print("\n[STEP 2] SENDING TEST EMAIL")
print("-" * 40)
try:
    result = send_mail(
        subject='PaperTrail - Test Email',
        message='This is a test email from PaperTrail to verify Gmail SMTP configuration.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
        fail_silently=False,
    )
    print(f"✅ Email sent successfully! Result: {result}")
    print(f"   Check inbox: {settings.EMAIL_HOST_USER}")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check if there are users with Gmail addresses
print("\n[STEP 3] CHECKING USERS WITH GMAIL")
print("-" * 40)
gmail_users = User.objects.filter(personal_email__iendswith='@gmail.com')
print(f"Found {gmail_users.count()} users with Gmail addresses:")
for user in gmail_users[:5]:
    print(f"  - {user.username}: {user.personal_email}")

# Test 4: Test password reset email for a specific user
print("\n[STEP 4] TEST PASSWORD RESET EMAIL")
print("-" * 40)
test_email = input("Enter Gmail address to test password reset (or press Enter to skip): ").strip()

if test_email:
    user = User.objects.filter(personal_email__iexact=test_email, is_active=True).first()
    
    if user:
        print(f"✓ Found user: {user.username}")
        print("Attempting to send password reset email...")
        
        try:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.template.loader import render_to_string
            from django.core.mail import EmailMessage
            
            # Generate token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Build context
            protocol = 'http' if settings.DEBUG else 'https'
            domain = settings.SITE_DOMAIN
            reset_url = f"{protocol}://{domain}/accounts/reset/{uid}/{token}/"
            
            print(f"\n📧 Reset Link: {reset_url}")
            
            # Send email
            subject = "PaperTrail - Password Reset Request"
            message = f"""Hello, {user.personal_email}

Please reset your password using the link below:
{reset_url}

This link will expire in 1 hour for security.

If you did not request this, ignore this email.

Best regards,
PaperTrail Team
"""
            
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.personal_email]
            )
            email.send(fail_silently=False)
            
            print(f"\n✅ Password reset email sent successfully!")
            print(f"   Check inbox: {user.personal_email}")
            
        except Exception as e:
            print(f"\n❌ Failed to send password reset email: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ No active user found with email: {test_email}")
else:
    print("⏭️  Skipped password reset test")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

print("\n📝 TROUBLESHOOTING TIPS:")
print("1. Make sure the Gmail App Password is correct (16 characters)")
print("2. Check Gmail settings: Allow less secure apps (or use App Password)")
print("3. Verify 2-Factor Authentication is enabled if using App Password")
print("4. Check spam/junk folder for the email")
print("5. Make sure SITE_DOMAIN is set correctly for password reset links")
