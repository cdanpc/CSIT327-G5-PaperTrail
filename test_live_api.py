"""
Real-time Forum API Test Script
Tests the live API endpoint while server is running
"""
import requests
import json
from datetime import datetime

print("=" * 80)
print("LIVE FORUM API TEST")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test 1: Unauthenticated Request
print("[TEST 1] Unauthenticated API Call")
print("-" * 40)
try:
    response = requests.get('http://127.0.0.1:8000/forum/api/topics/', timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Response Time: {response.elapsed.total_seconds():.3f}s")
    
    if response.status_code == 401:
        print("✓ Expected: Returns 401 (authentication required)")
        data = response.json()
        print(f"  Success: {data.get('success')}")
        print(f"  Error: {data.get('error')}")
        print(f"  Redirect: {data.get('redirect')}")
    else:
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Cannot connect to server!")
    print("   Make sure the Django server is running: python manage.py runserver")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Authenticated Request (with session)
print("\n[TEST 2] Authenticated API Call (with session)")
print("-" * 40)
try:
    # First, login to get session cookie
    session = requests.Session()
    
    # Get CSRF token
    response = session.get('http://127.0.0.1:8000/accounts/login/')
    csrf_token = None
    for cookie in session.cookies:
        if cookie.name == 'csrftoken':
            csrf_token = cookie.value
            break
    
    if not csrf_token:
        print("⚠ Could not get CSRF token, trying login anyway...")
    
    # Try to login (you'll need valid credentials)
    print("Attempting login...")
    login_data = {
        'username': 'jamparo',  # Replace with valid username
        'password': 'password',  # Replace with valid password
        'csrfmiddlewaretoken': csrf_token
    }
    
    login_response = session.post(
        'http://127.0.0.1:8000/accounts/login/',
        data=login_data,
        headers={'Referer': 'http://127.0.0.1:8000/accounts/login/'}
    )
    
    print(f"Login Status: {login_response.status_code}")
    
    # Now try the API with the authenticated session
    print("\nCalling API with authenticated session...")
    api_response = session.get('http://127.0.0.1:8000/forum/api/topics/')
    
    print(f"Status Code: {api_response.status_code}")
    print(f"Content-Type: {api_response.headers.get('Content-Type')}")
    print(f"Response Time: {api_response.elapsed.total_seconds():.3f}s")
    
    if api_response.status_code == 200:
        data = api_response.json()
        print("\n✅ SUCCESS!")
        print(f"  Success: {data.get('success')}")
        print(f"  Total Topics: {data.get('total_topics')}")
        print(f"  Topics Count: {len(data.get('topics', []))}")
        
        if data.get('topics'):
            print("\n📋 Topics List:")
            for topic in data['topics']:
                print(f"  - {topic['id']}: {topic['name']} ({topic['thread_count']} threads)")
    else:
        print(f"Response: {api_response.text[:500]}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check if server is responding
print("\n[TEST 3] Server Health Check")
print("-" * 40)
try:
    response = requests.get('http://127.0.0.1:8000/', timeout=5)
    print(f"✓ Server is responding: {response.status_code}")
except Exception as e:
    print(f"❌ Server not responding: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
print("\n📝 Instructions:")
print("1. Make sure Django server is running: python manage.py runserver")
print("2. Open browser to: http://127.0.0.1:8000/forum/")
print("3. Open browser console (F12) and check for JavaScript errors")
print("4. Check Network tab to see the /forum/api/topics/ request")
