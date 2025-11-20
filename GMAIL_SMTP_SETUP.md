# Gmail SMTP Configuration - Deployment Guide

## ✅ Local Configuration Complete

Your Django project is now successfully configured to use Gmail SMTP for sending emails!

### Current Configuration Status
- ✅ Gmail SMTP settings configured in `settings.py`
- ✅ Email credentials set in `.env` file
- ✅ Password reset form updated to accept Gmail only
- ✅ Test email sent successfully
- ✅ App Password formatted correctly (no spaces): `bjlltjvyymlauzip`

---

## 📋 Environment Variables

### Local Development (.env file)
Your `.env` file already has these correct values:

```env
EMAIL_HOST_USER=chrisdanielcabatana@gmail.com
EMAIL_HOST_PASSWORD=bjlltjvyymlauzip
```

---

## 🚀 Render Deployment Instructions

### Step 1: Add Environment Variables in Render

1. Go to your Render dashboard: https://dashboard.render.com/
2. Select your **PaperTrail** web service
3. Click on **Environment** in the left sidebar
4. Add the following environment variables:

| Key | Value |
|-----|-------|
| `EMAIL_HOST_USER` | `chrisdanielcabatana@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `bjlltjvyymlauzip` |

### Step 2: Save and Redeploy

1. Click **Save Changes** button
2. Render will automatically redeploy your service with the new environment variables
3. Wait for deployment to complete (usually 2-5 minutes)

### Step 3: Verify Deployment

After deployment completes, check the logs:
```
✅ Using Gmail SMTP with chrisdanielcabatana@gmail.com
```

If you see this message, Gmail SMTP is configured correctly!

---

## 🔐 Gmail Security Settings

### Requirements
- ✅ 2-Factor Authentication (2FA) must be enabled on your Gmail account
- ✅ App Password must be generated (not your regular Gmail password)
- ✅ App Password must be 16 characters with no spaces

### If Email Sending Fails

1. **Check 2FA is enabled:**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification if not already enabled

2. **Generate new App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select app: "Mail"
   - Select device: "Other (Custom name)" → type "PaperTrail"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)
   - **Remove all spaces**: `abcdefghijklmnop`
   - Update `EMAIL_HOST_PASSWORD` in both `.env` and Render

3. **Verify Gmail settings:**
   - Make sure "Less secure app access" is OFF (not needed with App Passwords)
   - Ensure your Gmail account is not locked or suspended

---

## 🧪 Testing Email Functionality

### Test Locally
Run the test script:
```bash
python test_email.py
```

### Test Password Reset Flow
1. Start your development server:
   ```bash
   python manage.py runserver
   ```

2. Go to: http://127.0.0.1:8000/accounts/forgot-password/

3. Enter a Gmail address that exists in your User database (in the `personal_email` field)

4. Check the Gmail inbox for the password reset email

5. Click the reset link and set a new password

---

## 📝 Configuration Details

### settings.py (Already Updated)
```python
# Gmail SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = f'PaperTrail <{EMAIL_HOST_USER}>'
```

### Password Reset Form (accounts/forms.py)
- ✅ Now accepts **Gmail only** (@gmail.com)
- ✅ Queries the `personal_email` field in User model
- ✅ Validates @gmail.com domain only

### Password Reset Template (password_reset_form.html)
- ✅ Updated labels: "Gmail Address"
- ✅ Updated placeholder: "your.email@gmail.com"
- ✅ Updated validation: Gmail only

---

## 🔄 Migration Notes

### What Changed
- ❌ Removed: Outlook/CITU SMTP configuration
- ❌ Removed: Support for @cit.edu emails in password reset
- ✅ Added: Gmail SMTP configuration
- ✅ Added: Gmail-only password reset (queries `personal_email` field)

### User Impact
- Users must use their Gmail address for password reset
- University email (@cit.edu) can still be stored in `univ_email` field
- Password reset emails are sent from: `PaperTrail <chrisdanielcabatana@gmail.com>`

---

## 🐛 Troubleshooting

### Error: "535 BadCredentials"
- App Password is incorrect or has spaces
- Solution: Regenerate App Password and update `.env`

### Error: "Username and Password not accepted"
- EMAIL_HOST_USER is not your full Gmail address
- Solution: Make sure it's `youremail@gmail.com` (not just username)

### Emails Not Arriving
- Check spam/junk folder
- Verify user has `personal_email` field set in database
- Check Render logs for error messages

### Console Backend in Development
If you see: `⚠️ Using console email backend`
- This means EMAIL_HOST_USER is not set
- Emails will print to terminal instead of sending
- Update your `.env` file with Gmail credentials

---

## ✨ Success Indicators

### You'll know it's working when:
1. Django system check passes: `python manage.py check`
2. Test email script succeeds: `python test_email.py`
3. Server logs show: `✅ Using Gmail SMTP with chrisdanielcabatana@gmail.com`
4. Password reset emails arrive in Gmail inbox
5. No SMTP authentication errors in logs

---

## 📞 Support

If you encounter issues:
1. Check Render logs: https://dashboard.render.com/ → Your Service → Logs
2. Run test script locally: `python test_email.py`
3. Verify environment variables are set in Render
4. Confirm 2FA is enabled on Gmail account
5. Generate a fresh App Password if needed

---

**Last Updated:** November 21, 2025  
**Status:** ✅ Gmail SMTP Configuration Complete and Tested
