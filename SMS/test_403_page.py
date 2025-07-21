#!/usr/bin/env python3
"""
Test script to verify that the 403 error page is working correctly.
This script tests that users get a proper 403 page with login options when accessing restricted URLs.
"""

import os
import sys
import django
import requests

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

def test_403_page():
    """Test that 403 page is displayed correctly for unauthorized access"""
    
    print("Testing 403 Access Denied Page...")
    print("=" * 50)
    
    # Create test client
    client = Client()
    
    # Test URLs that require admin access
    admin_urls = [
        '/dashboard/dashboard/',
        '/student/list/',
        '/staff/list/',
    ]
    
    print("\n1. Testing access without login (should redirect to login):")
    for url in admin_urls:
        try:
            response = client.get(url)
            if response.status_code == 302:
                print(f"✓ {url} - Redirected to login (302)")
            else:
                print(f"? {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"? {url} - Error: {str(e)}")
    
    # Create a regular user (non-admin)
    try:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        print(f"\n✓ Created test user: {user.username}")
    except Exception as e:
        print(f"\n? Error creating user: {str(e)}")
        # User might already exist, try to get it
        try:
            user = User.objects.get(username='testuser')
            print(f"✓ Using existing test user: {user.username}")
        except:
            print("✗ Could not create or find test user")
            return
    
    print("\n2. Testing access with regular user (should show 403 page):")
    client.login(username='testuser', password='testpass123')
    
    for url in admin_urls:
        try:
            response = client.get(url)
            if response.status_code == 403:
                print(f"✓ {url} - Access denied with 403 page")
                # Check if the response contains our custom 403 template content
                if b'Access Denied' in response.content and b'Login as Admin' in response.content:
                    print(f"  ✓ Custom 403 template is being used")
                else:
                    print(f"  ? Custom 403 template might not be loading correctly")
            else:
                print(f"? {url} - Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"? {url} - Error: {str(e)}")
    
    # Test with admin user
    try:
        admin_user = User.objects.create_superuser(
            username='testadmin',
            password='adminpass123',
            email='admin@example.com'
        )
        print(f"\n✓ Created test admin user: {admin_user.username}")
    except Exception as e:
        try:
            admin_user = User.objects.get(username='testadmin')
            print(f"\n✓ Using existing test admin user: {admin_user.username}")
        except:
            print(f"\n? Could not create or find admin user: {str(e)}")
            return
    
    print("\n3. Testing access with admin user (should work):")
    client.login(username='testadmin', password='adminpass123')
    
    for url in admin_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"✓ {url} - Access granted (200)")
            elif response.status_code == 302:
                print(f"✓ {url} - Redirected (302)")
            else:
                print(f"? {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"? {url} - Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo manually test:")
    print("1. Visit http://127.0.0.1:8000/dashboard/dashboard/ without logging in")
    print("2. Login with a regular user and try to access admin pages")
    print("3. You should see a nice 403 page with login options")

if __name__ == '__main__':
    test_403_page()
