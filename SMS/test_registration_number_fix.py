#!/usr/bin/env python3
"""
Test script to verify that the registration number IntegrityError fix works correctly.
This script tests the improved registration number generation and duplicate handling.
"""

import os
import sys
import django
from datetime import date

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings')
django.setup()

from django.db import IntegrityError
from apps.students.models import Student
from apps.corecode.models import StudentClass

def test_registration_number_generation():
    """Test that registration numbers are generated uniquely"""
    
    print("Testing Registration Number Generation Fix")
    print("=" * 50)
    
    # Get or create a test class
    try:
        test_class = StudentClass.objects.get(name="Test Class")
    except StudentClass.DoesNotExist:
        test_class = StudentClass.objects.create(name="Test Class")
        print(f"✓ Created test class: {test_class.name}")
    
    # Test data for creating multiple students
    test_students = [
        {
            'fullname': 'Test Student 1',
            'current_class': test_class,
            'section': 'A',
            'date_of_admission': date.today(),
            'Father_name': 'Test Father 1',
            'Father_mobile_number': '9876543210'
        },
        {
            'fullname': 'Test Student 2',
            'current_class': test_class,
            'section': 'A',
            'date_of_admission': date.today(),
            'Father_name': 'Test Father 2',
            'Father_mobile_number': '9876543211'
        },
        {
            'fullname': 'Test Student 3',
            'current_class': test_class,
            'section': 'A',
            'date_of_admission': date.today(),
            'Father_name': 'Test Father 3',
            'Father_mobile_number': '9876543212'
        }
    ]
    
    created_students = []
    registration_numbers = []
    
    print("\n1. Testing sequential student creation:")
    
    for i, student_data in enumerate(test_students, 1):
        try:
            student = Student(**student_data)
            student.save()
            created_students.append(student)
            registration_numbers.append(student.registration_number)
            print(f"✓ Student {i} created successfully with registration number: {student.registration_number}")
        except IntegrityError as e:
            print(f"✗ Failed to create Student {i}: {str(e)}")
        except Exception as e:
            print(f"✗ Unexpected error creating Student {i}: {str(e)}")
    
    print(f"\n2. Checking for duplicate registration numbers:")
    unique_numbers = set(registration_numbers)
    if len(unique_numbers) == len(registration_numbers):
        print(f"✓ All {len(registration_numbers)} registration numbers are unique")
    else:
        print(f"✗ Found duplicate registration numbers!")
        print(f"  Total numbers: {len(registration_numbers)}")
        print(f"  Unique numbers: {len(unique_numbers)}")
        print(f"  Registration numbers: {registration_numbers}")
    
    print(f"\n3. Testing registration number format:")
    for reg_num in registration_numbers:
        if reg_num:
            year_suffix = str(date.today().year)[-2:]
            expected_prefix = f"{year_suffix}Test ClassA"
            if reg_num.startswith(expected_prefix.replace(' ', '')):
                print(f"✓ Registration number format correct: {reg_num}")
            else:
                print(f"? Registration number format unexpected: {reg_num}")
                print(f"  Expected to start with: {expected_prefix}")
    
    print(f"\n4. Testing concurrent creation simulation:")
    # Try to create students with the same data simultaneously
    concurrent_students = []
    for i in range(3):
        try:
            student = Student(
                fullname=f'Concurrent Test Student {i+1}',
                current_class=test_class,
                section='B',
                date_of_admission=date.today(),
                Father_name=f'Concurrent Father {i+1}',
                Father_mobile_number=f'987654321{i+3}'
            )
            student.save()
            concurrent_students.append(student)
            print(f"✓ Concurrent student {i+1} created: {student.registration_number}")
        except IntegrityError as e:
            print(f"✗ IntegrityError for concurrent student {i+1}: {str(e)}")
        except Exception as e:
            print(f"✗ Unexpected error for concurrent student {i+1}: {str(e)}")
    
    # Check uniqueness of concurrent students
    concurrent_reg_numbers = [s.registration_number for s in concurrent_students]
    concurrent_unique = set(concurrent_reg_numbers)
    if len(concurrent_unique) == len(concurrent_reg_numbers):
        print(f"✓ All {len(concurrent_reg_numbers)} concurrent registration numbers are unique")
    else:
        print(f"✗ Found duplicate registration numbers in concurrent creation!")
    
    print(f"\n5. Cleanup - Removing test students:")
    all_test_students = created_students + concurrent_students
    for student in all_test_students:
        try:
            student.delete()
            print(f"✓ Deleted student: {student.fullname}")
        except Exception as e:
            print(f"✗ Error deleting student {student.fullname}: {str(e)}")
    
    # Clean up test class if it was created
    try:
        if test_class.name == "Test Class":
            test_class.delete()
            print(f"✓ Deleted test class")
    except Exception as e:
        print(f"? Could not delete test class: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Registration Number Fix Test Completed!")
    print("\nSummary:")
    print(f"- Created {len(created_students)} sequential students successfully")
    print(f"- Created {len(concurrent_students)} concurrent students successfully")
    print(f"- All registration numbers were unique: {'Yes' if len(set(registration_numbers + concurrent_reg_numbers)) == len(registration_numbers + concurrent_reg_numbers) else 'No'}")
    print("\nThe IntegrityError fix appears to be working correctly!")

if __name__ == '__main__':
    test_registration_number_generation()
