from decouple import config  # legacy fallback (can be removed later)
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
import dj_database_url
 
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
 
 
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
 
# Load .env in local development (Render sets RENDER=true in its environment)
if os.environ.get("RENDER", "") != "true":
    load_dotenv()
 
# Core settings from environment (fall back only for dev convenience)
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or os.environ.get("SECRET_KEY") or "unsafe-dev-key"
DEBUG = os.environ.get("DJANGO_DEBUG", os.environ.get("DEBUG", "False")).lower() == "true"
 
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
 
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1")).split(',') if h.strip()]
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
    if '.onrender.com' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('.onrender.com')
 
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", os.environ.get("CSRF_TRUSTED_ORIGINS", "")).split(',') if o.strip()]
if RENDER_EXTERNAL_HOSTNAME:
    host_origin = f"https://{RENDER_EXTERNAL_HOSTNAME}"
    if host_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(host_origin)
    wildcard_origin = 'https://*.onrender.com'
    if wildcard_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(wildcard_origin)
 
 
# Application definition
 
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
   
    # Local apps
    'accounts',
    'resources',
    'quizzes',
    'bookmarks',
    'flashcards',
 
    # Third-party apps
    "crispy_forms",
    "crispy_bootstrap5",
]
 
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.ForcePasswordChangeMiddleware',
    'accounts.middleware.UserRoleMiddleware',
    'accounts.middleware.SessionTrackingMiddleware',  # Track user sessions
]
 
ROOT_URLCONF = 'papertrail.urls'
 
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
 
WSGI_APPLICATION = 'papertrail.wsgi.application'
   
SUPABASE_URL = os.environ.get('SUPABASE_URL', config('SUPABASE_URL', default=''))
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', config('SUPABASE_SERVICE_KEY', default=''))
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', config('SUPABASE_BUCKET', default='papertrail-storage'))
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', config('SUPABASE_ANON_KEY', default=''))
SUPABASE_ANON_KEY = config('SUPABASE_ANON_KEY', default='')
 
# Use SQLite for local development, PostgreSQL for production
 
# Database (expects DATABASE_URL in Render or local .env)
DATABASE_URL = os.environ.get('DATABASE_URL') or config('DATABASE_URL', default=None)
DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        ssl_require=True
    )
}
 
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
 
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
 
 
# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
 
LANGUAGE_CODE = 'en-us'
 
TIME_ZONE = 'UTC'
 
USE_I18N = True
 
USE_TZ = True
 
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
 
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.User'
 
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'  # Landing page (home)
 
# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
 
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
 
# WhiteNoise static files storage (use manifest for cache busting)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
 
# Honor X-Forwarded-Proto header set by Render's proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
 
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
 
# Message settings
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.DEBUG: 'alert-secondary',
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger',
}
 
# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_PERMISSIONS = 0o644
 
# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_SAVE_EVERY_REQUEST = True
 
# Email settings - Gmail SMTP for production (sends actual emails)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')  # Gmail App Password from .env
DEFAULT_FROM_EMAIL = 'PaperTrail <noreply@papertrail.com>'
 
if os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "True").lower() == "true":
    SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
 
# Note: Using Gmail App Password from environment/.env file