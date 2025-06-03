from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.corecode.backup_utils import run_automated_backup
from apps.corecode.models import AutomatedBackupSettings


class Command(BaseCommand):
    help = 'Run automated backup if scheduled'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force backup regardless of schedule',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        try:
            settings = AutomatedBackupSettings.objects.first()
            if not settings:
                self.stdout.write(self.style.WARNING('No automated backup settings found'))
                return
            
            if not settings.enabled and not force:
                self.stdout.write(self.style.WARNING('Automated backups are disabled'))
                return
            
            now = timezone.now()
            if force or not settings.next_backup or now >= settings.next_backup:
                self.stdout.write(self.style.SUCCESS('Starting automated backup...'))
                backup = run_automated_backup()
                
                if backup:
                    self.stdout.write(self.style.SUCCESS(f'Backup created successfully: {backup.name}'))
                else:
                    self.stdout.write(self.style.ERROR('Failed to create backup'))
            else:
                next_backup = settings.next_backup
                time_remaining = next_backup - now
                hours, remainder = divmod(time_remaining.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                self.stdout.write(self.style.WARNING(
                    f'Next backup scheduled for {next_backup.strftime("%Y-%m-%d %H:%M:%S")} '
                    f'({int(hours)}h {int(minutes)}m {int(seconds)}s from now)'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
