#!/usr/bin/env python3
"""
Test script to verify admin access control is working properly.
This script tests that only admin users can access admin dashboard views.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.http import HttpResponseForbidden

User = get_user_model()

def test_admin_access_control():
    """Test that admin views are properly protected"""
    
    print("Testing admin access control...")
    
    # Create test client
    client = Client()
    
    # Create a regular user (non-admin)
    regular_user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        is_superuser=False,
        is_staff=False
    )
    
    # Create an admin user
    admin_user = User.objects.create_user(
        username='admin',
        password='adminpass123',
        is_superuser=True,
        is_staff=True
    )
    
    # Test URLs that should be admin-only
    admin_urls = [
        '/dashboard/dashboard/',  # Main admin dashboard
        '/student/list',          # Student management
        '/staff/list/',           # Staff management
        '/fees/',                 # Fee management
        '/transport/',            # Transport management
        '/dashboard/system-settings/',  # System settings
    ]
    
    print("\n1. Testing access with regular user (should be denied):")
    client.login(username='testuser', password='testpass123')
    
    for url in admin_urls:
        try:
            response = client.get(url)
            if response.status_code == 403:
                print(f"✓ {url} - Access denied (403)")
            elif response.status_code == 302:
                print(f"✓ {url} - Redirected (302)")
            else:
                print(f"✗ {url} - Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"? {url} - Error: {str(e)}")
    
    print("\n2. Testing access with admin user (should be allowed):")
    client.login(username='admin', password='adminpass123')
    
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
    
    print("\n3. Testing unauthenticated access (should be denied):")
    client.logout()
    
    for url in admin_urls:
        try:
            response = client.get(url)
            if response.status_code == 302:
                print(f"✓ {url} - Redirected to login (302)")
            elif response.status_code == 403:
                print(f"✓ {url} - Access denied (403)")
            else:
                print(f"? {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"? {url} - Error: {str(e)}")
    
    # Clean up test users
    regular_user.delete()
    admin_user.delete()
    
    print("\nAdmin access control test completed!")

if __name__ == '__main__':
    test_admin_access_control()
