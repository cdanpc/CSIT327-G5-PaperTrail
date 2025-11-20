"""
Script to manually create the accounts_notification table
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.db import connection

def create_notification_table():
    with connection.cursor() as cursor:
        # Create the accounts_notification table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts_notification (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                url VARCHAR(200),
                is_read BOOLEAN DEFAULT FALSE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                related_object_type VARCHAR(50),
                related_object_id INTEGER,
                CONSTRAINT accounts_notification_user_id_fk 
                    FOREIGN KEY (user_id) REFERENCES accounts_user(id) 
                    ON DELETE CASCADE
            );
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS accounts_notification_user_created_idx 
                ON accounts_notification(user_id, created_at DESC);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS accounts_notification_user_read_idx 
                ON accounts_notification(user_id, is_read);
        """)
        
        print("✓ Table accounts_notification created successfully!")
        print("✓ Indexes created successfully!")

try:
    create_notification_table()
except Exception as e:
    print(f"Error creating table: {e}")
