"""
Test script to verify Gmail SMTP configuration
Run this with: python test_email.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_gmail_smtp():
    print("\n" + "="*70)
    print("GMAIL SMTP CONFIGURATION TEST")
    print("="*70)
    
    # Show current configuration
    print("\n📧 Current Email Settings:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"   From Email: {settings.EMAIL_HOST_USER}")
    print(f"   Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    # Check if credentials are set
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        print("\n❌ ERROR: Email credentials not set in .env file!")
        return False
    
    # Try to send a test email
    print("\n📨 Sending test email...")
    try:
        result = send_mail(
            subject='PaperTrail - Gmail SMTP Test',
            message='This is a test email to verify Gmail SMTP configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False,
        )
        
        if result == 1:
            print(f"\n✅ SUCCESS! Test email sent to {settings.EMAIL_HOST_USER}")
            print("\n📬 Check your Gmail inbox (including spam folder)")
            print("\n" + "="*70)
            return True
        else:
            print(f"\n❌ FAILED: send_mail returned {result}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        print("\n🔍 Possible causes:")
        print("   1. App Password is incorrect")
        print("   2. Gmail address is wrong")
        print("   3. 2-Factor Authentication not enabled on Gmail")
        print("   4. App Password not generated correctly")
        print("\n💡 Solution:")
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Generate a new 16-character App Password")
        print("   3. Update EMAIL_HOST_PASSWORD in .env (no spaces)")
        print("   4. Make sure 2FA is enabled on your Gmail account")
        print("\n" + "="*70)
        return False

if __name__ == '__main__':
    test_gmail_smtp()
