"""
Script to check if notification table exists and create it if missing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def check_table_exists():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'accounts_notification'
        """)
        result = cursor.fetchall()
        return len(result) > 0

print("Checking if accounts_notification table exists...")
exists = check_table_exists()

if exists:
    print("✓ Table accounts_notification EXISTS")
else:
    print("✗ Table accounts_notification DOES NOT EXIST")
    print("\nAttempting to create the table by running migrations...")
    
    # Unapply the migration first
    print("\n1. Unapplying accounts.0001_initial migration...")
    call_command('migrate', 'accounts', 'zero', '--fake')
    
    # Reapply it
    print("\n2. Reapplying accounts.0001_initial migration...")
    call_command('migrate', 'accounts')
    
    # Check again
    print("\n3. Checking if table was created...")
    exists_now = check_table_exists()
    if exists_now:
        print("✓ SUCCESS! Table accounts_notification was created")
    else:
        print("✗ FAILED! Table still doesn't exist")

print("\nDone!")
