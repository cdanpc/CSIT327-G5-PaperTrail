import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from accounts.models import User

print("=" * 80)
print("ALL USERS IN DATABASE")
print("=" * 80)

users = User.objects.all()
print(f"\nTotal users: {users.count()}\n")

for user in users:
    print(f"Username: {user.username:20} | Student ID: {user.stud_id or 'None':15} | Email: {user.personal_email}")

print("\n" + "=" * 80)
print("STUDENTS ONLY (with Student IDs)")
print("=" * 80)

students = User.objects.filter(stud_id__isnull=False)
print(f"\nTotal students with IDs: {students.count()}\n")

for student in students:
    print(f"Username: {student.username:20} | Student ID: {student.stud_id:15} | Name: {student.get_display_name()}")

print("\n" + "=" * 80)
