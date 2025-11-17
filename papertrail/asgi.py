"""
ASGI config for PaperTrail project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# IMPORTANT: module names are case-sensitive on Linux
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')

application = get_asgi_application()
