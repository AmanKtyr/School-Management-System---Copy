from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.staffs.models import Staff
from datetime import date

class Command(BaseCommand):
    help = 'Create a test teacher account for testing purposes'

    def handle(self, *args, **options):
        # Check if test teacher already exists
        if Staff.objects.filter(fullname='Test Teacher').exists():
            self.stdout.write(
                self.style.WARNING('Test teacher already exists!')
            )
            staff = Staff.objects.get(fullname='Test Teacher')
            self.stdout.write(f'Login ID: {staff.staff_login_id}')
            self.stdout.write(f'Password: {staff.staff_password}')
            return

        # Create test teacher
        try:
            staff = Staff.objects.create(
                fullname='Test Teacher',
                gender='male',
                date_of_birth=date(1985, 5, 15),
                date_of_registration=date.today(),
                mobile_number='9876543210',
                aadhar='123456789012',
                Subject_specification='Mathematics, Science',
                address='123 Teacher Street, Education City',
                others='Test teacher account for demonstration purposes',
                current_status='active'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created test teacher: {staff.fullname}')
            )
            self.stdout.write(f'Registration Number: {staff.registration_number}')
            self.stdout.write(f'Login ID: {staff.staff_login_id}')
            self.stdout.write(f'Password: {staff.staff_password}')
            self.stdout.write(
                self.style.SUCCESS('You can now login as a teacher using these credentials!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test teacher: {str(e)}')
            )
