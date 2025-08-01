from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from apps.notice.models import Notice, NoticeCategory, NoticeRecipient


class Command(BaseCommand):
    help = 'Create sample notices for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample notice categories...')
        
        # Create categories
        categories = [
            {'name': 'Academic', 'description': 'Academic related notices', 'color': '#007bff'},
            {'name': 'Events', 'description': 'School events and activities', 'color': '#28a745'},
            {'name': 'Holidays', 'description': 'Holiday announcements', 'color': '#ffc107'},
            {'name': 'Urgent', 'description': 'Urgent announcements', 'color': '#dc3545'},
            {'name': 'General', 'description': 'General information', 'color': '#6c757d'},
        ]
        
        for cat_data in categories:
            category, created = NoticeCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Get or create admin user
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@school.com',
                password='admin123'
            )
            self.stdout.write('Created admin user')
        
        # Sample notices
        sample_notices = [
            {
                'title': 'Welcome to New Academic Year 2024-25',
                'content': '''Dear Students and Staff,

We are pleased to welcome everyone to the new academic year 2024-25. This year brings new opportunities, challenges, and exciting learning experiences.

Key highlights for this year:
- New curriculum updates
- Enhanced digital learning platforms
- Improved infrastructure
- Additional extracurricular activities

We look forward to a successful and productive year ahead.

Best regards,
Principal''',
                'priority': 'high',
                'recipient_type': 'all',
                'category': 'Academic',
                'is_important': True,
            },
            {
                'title': 'Annual Sports Day - Registration Open',
                'content': '''The Annual Sports Day is scheduled for next month. All students are encouraged to participate in various sporting events.

Registration is now open for:
- Track and Field events
- Team sports (Football, Basketball, Volleyball)
- Individual competitions (Chess, Table Tennis)

Registration deadline: End of this week
Venue: School Sports Complex

For more information, contact the Sports Department.''',
                'priority': 'medium',
                'recipient_type': 'students',
                'category': 'Events',
            },
            {
                'title': 'Parent-Teacher Meeting Schedule',
                'content': '''Dear Parents,

The quarterly Parent-Teacher meeting is scheduled for the upcoming weekend. This is an important opportunity to discuss your child's academic progress and development.

Schedule:
- Saturday: Classes 1-5 (9:00 AM - 12:00 PM)
- Sunday: Classes 6-12 (9:00 AM - 1:00 PM)

Please confirm your attendance with the class teacher.

Thank you for your cooperation.''',
                'priority': 'high',
                'recipient_type': 'all',
                'category': 'Academic',
            },
            {
                'title': 'Holiday Notice - Gandhi Jayanti',
                'content': '''This is to inform all students and staff that the school will remain closed on October 2nd in observance of Gandhi Jayanti.

The school will resume normal operations from October 3rd.

Have a peaceful holiday!''',
                'priority': 'medium',
                'recipient_type': 'all',
                'category': 'Holidays',
            },
            {
                'title': 'Staff Meeting - Curriculum Updates',
                'content': '''All teaching staff are requested to attend the mandatory staff meeting scheduled for tomorrow.

Agenda:
- New curriculum guidelines
- Assessment methods update
- Digital tools training
- Q&A session

Time: 2:00 PM - 4:00 PM
Venue: Main Conference Hall

Attendance is mandatory.''',
                'priority': 'urgent',
                'recipient_type': 'teachers',
                'category': 'Academic',
                'is_important': True,
            },
        ]
        
        self.stdout.write('Creating sample notices...')
        
        for notice_data in sample_notices:
            category_name = notice_data.pop('category', None)
            category = None
            if category_name:
                category = NoticeCategory.objects.filter(name=category_name).first()
            
            notice = Notice.objects.create(
                created_by=admin_user,
                status='published',
                valid_from=timezone.now(),
                valid_until=timezone.now() + timedelta(days=30),
                category=category,
                **notice_data
            )
            
            # Create recipients based on recipient type
            self.create_recipients(notice)
            
            self.stdout.write(f'Created notice: {notice.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample notices!')
        )
    
    def create_recipients(self, notice):
        """Create recipients for the notice"""
        recipients = []
        
        if notice.recipient_type == 'all':
            users = User.objects.filter(is_active=True)
            recipients = [NoticeRecipient(notice=notice, user=user) for user in users]
        elif notice.recipient_type == 'students':
            # For now, get non-staff users (assuming they are students)
            users = User.objects.filter(is_active=True, is_staff=False, is_superuser=False)
            recipients = [NoticeRecipient(notice=notice, user=user) for user in users]
        elif notice.recipient_type == 'teachers':
            # Get staff users
            users = User.objects.filter(is_active=True, is_staff=True, is_superuser=False)
            recipients = [NoticeRecipient(notice=notice, user=user) for user in users]
        
        if recipients:
            NoticeRecipient.objects.bulk_create(recipients)
