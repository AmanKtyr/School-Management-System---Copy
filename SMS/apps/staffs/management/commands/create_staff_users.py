from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import Staff

class Command(BaseCommand):
    help = 'Create User accounts for all Staff records that don\'t have one.'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for staff in Staff.objects.all():
            if staff.staff_login_id and staff.staff_password:
                if not staff.user:
                    try:
                        # Create new user
                        user = User.objects.create_user(
                            username=staff.staff_login_id,
                            password=staff.staff_password,
                            first_name=staff.fullname.split()[0] if staff.fullname else '',
                            last_name=' '.join(staff.fullname.split()[1:]) if len(staff.fullname.split()) > 1 else '',
                            is_staff=True,
                            is_active=True
                        )
                        staff.user = user
                        staff.save()
                        created_count += 1
                        self.stdout.write(f'Created user for staff: {staff.fullname} (Username: {staff.staff_login_id})')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error creating user for staff {staff.fullname}: {e}'))
                else:
                    # Update existing user credentials
                    try:
                        staff.user.username = staff.staff_login_id
                        staff.user.set_password(staff.staff_password)
                        staff.user.first_name = staff.fullname.split()[0] if staff.fullname else ''
                        staff.user.last_name = ' '.join(staff.fullname.split()[1:]) if len(staff.fullname.split()) > 1 else ''
                        staff.user.save()
                        updated_count += 1
                        self.stdout.write(f'Updated user for staff: {staff.fullname} (Username: {staff.staff_login_id})')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error updating user for staff {staff.fullname}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new User accounts and updated {updated_count} existing accounts for Staff.'))