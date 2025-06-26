from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import Staff

class Command(BaseCommand):
    help = 'Create missing User objects for all Staff records.'

    def handle(self, *args, **options):
        created_count = 0
        for staff in Staff.objects.all():
            if not staff.user:
                user = User.objects.create_user(
                    username=staff.staff_login_id,
                    password=staff.staff_password,
                    first_name=staff.fullname,
                )
                staff.user = user
                staff.save()
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} User objects for Staff.')) 