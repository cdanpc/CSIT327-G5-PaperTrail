import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from accounts.models import User

# Update professor IDs
try:
    frevilleza = User.objects.get(username='frevilleza')
    frevilleza.stud_id = '2050'
    frevilleza.save()
    print(f'✓ Updated: {frevilleza.username} -> Professor ID: {frevilleza.stud_id}')
except User.DoesNotExist:
    print('✗ User frevilleza not found')

try:
    jamparo = User.objects.get(username='jamparo')
    jamparo.stud_id = '2152'
    jamparo.save()
    print(f'✓ Updated: {jamparo.username} -> Professor ID: {jamparo.stud_id}')
except User.DoesNotExist:
    print('✗ User jamparo not found')

print('\nAll professor IDs updated successfully!')
print('\nCurrent professor IDs:')
professors = User.objects.filter(is_professor=True)
for prof in professors:
    print(f'  {prof.username}: {prof.stud_id or "No ID"}')
