"""
Management command to migrate existing users to have separate stud_id and univ_email fields.

This command updates users who registered before the field separation was implemented.
It ensures that:
1. Users with Student ID format usernames get their stud_id field populated
2. Users can be prompted to add their university email if missing

Run with: python manage.py migrate_user_fields
"""

from django.core.management.base import BaseCommand
from accounts.models import User
import re


class Command(BaseCommand):
    help = 'Migrate existing users to populate stud_id and univ_email fields separately'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Automatically migrate without confirmation',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('User Field Migration Tool'))
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write('')

        # Find users with missing stud_id field
        users_missing_stud_id = User.objects.filter(stud_id__isnull=True)
        
        if not users_missing_stud_id.exists():
            self.stdout.write(self.style.SUCCESS('✅ All users already have stud_id populated!'))
            return

        self.stdout.write(f'Found {users_missing_stud_id.count()} users with missing stud_id field:')
        self.stdout.write('')

        # Pattern for Student ID format: ##-####-###
        stud_id_pattern = r'^\d{2}-\d{4}-\d{3}$'
        
        updates = []
        for user in users_missing_stud_id:
            # Check if username matches Student ID format
            if re.fullmatch(stud_id_pattern, user.username):
                updates.append({
                    'user': user,
                    'username': user.username,
                    'action': 'Set stud_id from username',
                    'stud_id': user.username,
                    'univ_email': user.univ_email or 'Not set'
                })
                self.stdout.write(
                    f'  • {user.username} ({user.get_full_name()}) - Will populate stud_id'
                )
            else:
                self.stdout.write(
                    f'  • {user.username} ({user.get_full_name()}) - ⚠️ Username not in Student ID format, skipping'
                )

        if not updates:
            self.stdout.write(self.style.WARNING('\n⚠️ No users found with Student ID format usernames to migrate.'))
            return

        self.stdout.write('')
        self.stdout.write(f'Ready to update {len(updates)} users.')
        self.stdout.write('')

        # Confirm unless --auto flag is used
        if not options['auto']:
            confirm = input('Do you want to proceed? (yes/no): ')
            if confirm.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.WARNING('Migration cancelled.'))
                return

        # Perform migration
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Migrating users...'))
        self.stdout.write('')

        success_count = 0
        for update_info in updates:
            user = update_info['user']
            try:
                # Populate stud_id from username
                user.stud_id = update_info['stud_id']
                
                # If univ_email is not set, construct it from username
                # Format: username@cit.edu (e.g., 23-4223-156@cit.edu)
                if not user.univ_email:
                    # You can choose to skip this or set a default pattern
                    # For now, we'll leave it as None and let users update it in their profile
                    pass
                
                user.save()
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {user.username} - stud_id field populated')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ {user.username} - Error: {str(e)}')
                )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'✅ Migration complete! Updated {success_count}/{len(updates)} users.'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        
        # Show remaining users with missing univ_email
        missing_email = User.objects.filter(univ_email__isnull=True).count()
        if missing_email > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'ℹ️  Note: {missing_email} users still have missing university email. '
                    'They can update this in their profile page.'
                )
            )
