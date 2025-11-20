#!/usr/bin/env python
"""
Quick script to verify all registered URL patterns in the Django project.
Run: python check_urls.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def show_urls(UrlConf, namespace=None, prefix=''):
    """Recursively show all URL patterns"""
    if isinstance(UrlConf, URLResolver):
        patterns = UrlConf.url_patterns
        for pattern in patterns:
            if isinstance(pattern, URLResolver):
                # Nested URLconf (included urls)
                new_namespace = pattern.namespace or namespace
                show_urls(pattern, new_namespace, prefix + str(pattern.pattern))
            elif isinstance(pattern, URLPattern):
                # Individual URL pattern
                name = pattern.name
                if namespace:
                    full_name = f"{namespace}:{name}"
                else:
                    full_name = name
                
                url = prefix + str(pattern.pattern)
                print(f"{url:50} -> {full_name or '(no name)'}")

print("=" * 80)
print("REGISTERED URLS IN YOUR PROJECT")
print("=" * 80)
print("\n🔍 Forum URLs:\n")

resolver = get_resolver()
for pattern in resolver.url_patterns:
    if hasattr(pattern, 'namespace') and pattern.namespace == 'forum':
        show_urls(pattern, pattern.namespace, str(pattern.pattern))

print("\n" + "=" * 80)
print("✅ To use in templates: {% url 'namespace:pattern_name' %}")
print("=" * 80)
