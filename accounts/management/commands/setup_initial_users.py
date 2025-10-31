from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Sets up initial users (admin and professors)'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Create admin user
            if not User.objects.filter(username='citAdmin').exists():
                admin_user = User.objects.create_superuser(
                    username='citAdmin',
                    password='Wildcats2025',
                    email='admin@cit.edu',
                    first_name='CIT',
                    last_name='Admin',
                    personal_email='admin@cit.edu',
                    univ_email='admin@cit.edu',
                )
                self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.username}'))
            else:
                self.stdout.write(self.style.WARNING('Admin user already exists.'))

            professors_data = [
                {
                    'username': 'jamparo',
                    'password': '123456',
                    'stud_id': '2152',
                    'first_name': 'Joe Marie',
                    'last_name': 'Amparo',
                    'personal_email': 'joemarie.amparo@gmail.com',
                    'univ_email': 'joemarie.amparo@cit.edu',
                },
                {
                    'username': 'frevilleza',
                    'password': '123456',
                    'stud_id': '2050',
                    'first_name': 'Frederick',
                    'last_name': 'Revilleza',
                    'personal_email': 'frederick.revilleza@gmail.com',
                    'univ_email': 'frederick.revilleza@cit.edu',
                }
            ]

            for prof_data in professors_data:
                if User.objects.filter(username=prof_data['username']).exists():
                    self.stdout.write(self.style.WARNING(f"Professor {prof_data['username']} already exists."))
                    continue
                professor = User.objects.create_user(
                    username=prof_data['username'],
                    password=prof_data['password'],
                    stud_id=prof_data['stud_id'],
                    first_name=prof_data['first_name'],
                    last_name=prof_data['last_name'],
                    personal_email=prof_data['personal_email'],
                    univ_email=prof_data['univ_email'],
                    is_professor=True,
                    must_change_password=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created professor user: {professor.username} (ID: {professor.stud_id})'))