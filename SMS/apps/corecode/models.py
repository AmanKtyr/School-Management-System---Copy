from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import os

# Create your models here.


class SiteConfig(models.Model):
    """Site Configurations"""

    key = models.SlugField(unique=True)
    value = models.CharField(max_length=200)

    # New fields for site configuration
    college_name = models.CharField(max_length=200, blank=True, null=True)
    college_address = models.TextField(blank=True, null=True)
    college_email = models.EmailField(blank=True, null=True)
    college_phone = models.CharField(max_length=15, blank=True, null=True)
    college_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    principal_name = models.CharField(max_length=200, blank=True, null=True)
    COLLEGE_TYPE_CHOICES = [
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Semi-Government', 'Semi-Government'),
    ]
    college_type = models.CharField(
        max_length=20, choices=COLLEGE_TYPE_CHOICES, blank=True, null=True
    )

    def __str__(self):
        return self.key


class AcademicSession(models.Model):
    """Academic Session"""

    name = models.CharField(max_length=200, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class AcademicTerm(models.Model):
    """Academic Term"""

    name = models.CharField(max_length=20, unique=True)
    current = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Subject(models.Model):
    """Subject"""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentClass(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ClassSubject(models.Model):
    """Association between Class and Subject"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='class_subjects')
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='class_subjects')
    section = models.CharField(max_length=10, blank=True, null=True)
    teacher = models.ForeignKey('staffs.Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_subjects')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_class__name', 'subject__name']
        unique_together = ['subject', 'student_class', 'section']
        verbose_name = 'Class Subject'
        verbose_name_plural = 'Class Subjects'

    def __str__(self):
        section_str = f" - {self.section}" if self.section else ""
        return f"{self.subject.name} - {self.student_class.name}{section_str}"


class CollegeProfile(models.Model):
    college_name = models.CharField(max_length=255)
    college_address = models.TextField()
    college_email = models.EmailField()
    college_phone = models.CharField(max_length=15)
    college_logo = models.ImageField(upload_to='college_logos/', blank=True, null=True)
    established_year = models.PositiveIntegerField()
    principal_name = models.CharField(max_length=255)
    college_type = models.CharField(max_length=50, choices=[
        ('Government', 'Government'),
        ('Private', 'Private'),
        ('Semi-Government', 'Semi-Government'),
    ])
    admin_email = models.EmailField()
    admin_contact = models.CharField(max_length=15)
    facebook_link = models.URLField(blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.college_name




# fees settings
class FeeSettings(models.Model):
    class_name = models.ForeignKey('StudentClass', on_delete=models.CASCADE)
    section = models.CharField(max_length=20)
    frequency = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_name', 'section']

    def __str__(self):
        return f"{self.class_name} - {self.section}"

    def get_total_fees(self):
        return sum(fee.amount - fee.discount for fee in self.fees.all())

class FeeStructure(models.Model):
    fee_settings = models.ForeignKey(FeeSettings, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.fee_type} - {self.fee_settings}"


class Section(models.Model):
    """Model for class sections"""
    name = models.CharField(max_length=10)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='sections')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_class__name', 'name']
        unique_together = ['student_class', 'name']
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'

    def __str__(self):
        return f"{self.student_class.name} - {self.name}"


class ClassTeacher(models.Model):
    """Model for assigning class teachers to classes and sections"""
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='class_teachers')
    section = models.CharField(max_length=10, blank=True, null=True)
    teacher = models.ForeignKey('staffs.Staff', on_delete=models.CASCADE, related_name='assigned_classes')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student_class__name', 'section']
        unique_together = ['student_class', 'section']
        verbose_name = 'Class Teacher'
        verbose_name_plural = 'Class Teachers'

    def __str__(self):
        section_str = f" - {self.section}" if self.section else ""
        return f"{self.student_class.name}{section_str} - {self.teacher.fullname}"

class Backup(models.Model):
    """Model for storing backup metadata"""
    BACKUP_TYPE_CHOICES = [
        ('full', 'Full Backup'),
        ('database', 'Database Only'),
        ('media', 'Media Files Only'),
        ('settings', 'Settings Only'),
        ('custom', 'Custom Backup'),
    ]

    FORMAT_CHOICES = [
        ('zip', 'ZIP Archive'),
        ('sql', 'SQL Dump'),
        ('json', 'JSON Format'),
    ]

    name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    size = models.CharField(max_length=20)  # Store as string like "24.5 MB"
    size_bytes = models.BigIntegerField(default=0)  # Store actual size in bytes
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    is_encrypted = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    # Fields to track what was included in custom backups
    includes_students = models.BooleanField(default=True)
    includes_staff = models.BooleanField(default=True)
    includes_classes = models.BooleanField(default=True)
    includes_results = models.BooleanField(default=True)
    includes_attendance = models.BooleanField(default=True)
    includes_fees = models.BooleanField(default=True)
    includes_settings = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Backup'
        verbose_name_plural = 'Backups'

    def __str__(self):
        return f"{self.name} ({self.get_backup_type_display()}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def delete(self, *args, **kwargs):
        # Delete the actual file when the model instance is deleted
        if os.path.exists(self.file_path):
            try:
                os.remove(self.file_path)
            except Exception as e:
                print(f"Error deleting backup file: {e}")
        super().delete(*args, **kwargs)


class AutomatedBackupSettings(models.Model):
    """Model for automated backup settings"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
    ]

    BACKUP_TYPE_CHOICES = [
        ('full', 'Full Backup'),
        ('database', 'Database Only'),
        ('incremental', 'Incremental Backup'),
    ]

    RETENTION_CHOICES = [
        ('5', 'Keep last 5 backups'),
        ('10', 'Keep last 10 backups'),
        ('20', 'Keep last 20 backups'),
        ('all', 'Keep all backups'),
    ]

    enabled = models.BooleanField(default=False)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    backup_time = models.TimeField(default=timezone.now)
    day_of_week = models.IntegerField(default=0)  # 0=Sunday, 1=Monday, etc.
    backup_type = models.CharField(max_length=20, choices=BACKUP_TYPE_CHOICES, default='full')
    retention_policy = models.CharField(max_length=10, choices=RETENTION_CHOICES, default='10')
    notify_on_backup = models.BooleanField(default=True)
    last_backup = models.DateTimeField(null=True, blank=True)
    next_backup = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Automated Backup Settings'
        verbose_name_plural = 'Automated Backup Settings'

    def __str__(self):
        return f"Automated Backup ({self.get_frequency_display()})"

    def save(self, *args, **kwargs):
        # Calculate next backup time when saving
        if self.enabled and not self.next_backup:
            self.calculate_next_backup()
        super().save(*args, **kwargs)

    def calculate_next_backup(self):
        """Calculate the next backup time based on frequency settings"""
        now = timezone.now()
        backup_time = timezone.make_aware(timezone.datetime.combine(
            now.date(), self.backup_time
        ))

        if self.frequency == 'daily':
            # If today's backup time has passed, schedule for tomorrow
            if now > backup_time:
                self.next_backup = backup_time + timezone.timedelta(days=1)
            else:
                self.next_backup = backup_time

        elif self.frequency == 'weekly':
            # Calculate days until the next occurrence of day_of_week
            days_ahead = self.day_of_week - now.weekday()
            if days_ahead < 0 or (days_ahead == 0 and now > backup_time):
                days_ahead += 7

            next_day = now.date() + timezone.timedelta(days=days_ahead)
            self.next_backup = timezone.make_aware(timezone.datetime.combine(
                next_day, self.backup_time
            ))

        elif self.frequency == 'biweekly':
            # Similar to weekly but every two weeks
            days_ahead = self.day_of_week - now.weekday()
            if days_ahead < 0 or (days_ahead == 0 and now > backup_time):
                days_ahead += 14
            else:
                days_ahead = days_ahead % 14

            next_day = now.date() + timezone.timedelta(days=days_ahead)
            self.next_backup = timezone.make_aware(timezone.datetime.combine(
                next_day, self.backup_time
            ))

        elif self.frequency == 'monthly':
            # Schedule for the same day next month
            next_month = now.replace(day=1)
            if now.month == 12:
                next_month = next_month.replace(year=now.year + 1, month=1)
            else:
                next_month = next_month.replace(month=now.month + 1)

            # Adjust for months with fewer days
            try:
                next_month = next_month.replace(day=now.day)
            except ValueError:
                # If the day doesn't exist in the next month, use the last day
                if now.month == 12:
                    next_month = next_month.replace(year=now.year + 1, month=1, day=1) - timezone.timedelta(days=1)
                else:
                    next_month = next_month.replace(month=now.month + 1, day=1) - timezone.timedelta(days=1)

            self.next_backup = timezone.make_aware(timezone.datetime.combine(
                next_month.date(), self.backup_time
            ))
