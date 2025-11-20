"""
Test script to debug forum API endpoints
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'papertrail.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a test client
client = Client()

# Get a user to login with
user = User.objects.first()
if not user:
    print("❌ No users found in database!")
    exit(1)

print(f"✓ Found user: {user.username}")

# Login
client.force_login(user)
print(f"✓ Logged in as {user.username}")

# Test the API endpoint
print("\n🔍 Testing /forum/api/topics/ endpoint...")
response = client.get('/forum/api/topics/')

print(f"Status Code: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")

if response.status_code == 200:
    import json
    data = response.json()
    print(f"\n✅ API Response:")
    print(f"   Success: {data.get('success')}")
    print(f"   Topics Count: {len(data.get('topics', []))}")
    if data.get('topics'):
        print(f"   First Topic: {data['topics'][0].get('name')}")
    print(f"\n📦 Full Response:")
    print(json.dumps(data, indent=2))
else:
    print(f"❌ Error: {response.status_code}")
    print(f"Response: {response.content.decode()}")
