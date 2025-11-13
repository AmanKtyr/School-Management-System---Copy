#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings')
django.setup()

try:
    from apps.notice.models import Notice, NoticeRecipient, NoticeCategory
    print("✓ Models imported successfully!")
    
    # Test model creation
    print("✓ Notice model:", Notice)
    print("✓ NoticeRecipient model:", NoticeRecipient)
    print("✓ NoticeCategory model:", NoticeCategory)
    
    print("\nAll notice models are working correctly!")
    
except Exception as e:
    print(f"✗ Error importing models: {e}")
    import traceback
    traceback.print_exc()
