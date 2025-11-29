import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.db import connection

# Manually mark accounts.0001_initial as applied
with connection.cursor() as cursor:
    cursor.execute("""
        INSERT INTO django_migrations (app, name, applied) 
        VALUES ('accounts', '0001_initial', CURRENT_TIMESTAMP)
        ON CONFLICT DO NOTHING
    """)
    print("✅ Marked accounts.0001_initial as applied")

print("Migration history fixed!")
