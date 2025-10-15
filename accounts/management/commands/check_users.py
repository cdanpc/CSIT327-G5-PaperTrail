from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Display all users with their student IDs'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Total users: {users.count()} ===\n'))
        
        for user in users:
            user_type = []
            if user.is_superuser:
                user_type.append('SUPERUSER')
            if user.is_staff:
                user_type.append('STAFF')
            if user.is_professor:
                user_type.append('PROFESSOR')
            
            type_str = f" [{', '.join(user_type)}]" if user_type else " [STUDENT]"
            stud_id_str = user.stud_id if user.stud_id else "No ID"
            
            self.stdout.write(
                f"{user.username:15} | ID: {stud_id_str:15} | {user.email:30}{type_str}"
            )
        
        self.stdout.write(self.style.SUCCESS(f'\n=== End of user list ===\n'))
