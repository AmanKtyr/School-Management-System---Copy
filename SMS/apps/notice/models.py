from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass


class Notice(models.Model):
    """
    Model for storing notices that can be sent to students, teachers, and staff
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    RECIPIENT_TYPE_CHOICES = [
        ('all', 'All Users'),
        ('students', 'All Students'),
        ('teachers', 'All Teachers'),
        ('staff', 'All Staff'),
        ('class', 'Specific Class'),
        ('individual', 'Individual Users'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notices')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Recipient configuration
    recipient_type = models.CharField(max_length=15, choices=RECIPIENT_TYPE_CHOICES, default='all')
    target_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, null=True, blank=True,
                                   help_text="Select class if recipient type is 'Specific Class'")

    # Notice validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True,
                                     help_text="Leave blank for no expiry")

    # Additional options
    send_email = models.BooleanField(default=False, help_text="Send email notification")
    send_sms = models.BooleanField(default=False, help_text="Send SMS notification")
    is_important = models.BooleanField(default=False, help_text="Mark as important notice")

    # File attachment
    attachment = models.FileField(upload_to='notices/attachments/', null=True, blank=True)

    # Category
    category = models.ForeignKey('NoticeCategory', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'

    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"

    def get_absolute_url(self):
        return reverse('notice:detail', kwargs={'pk': self.pk})

    @property
    def is_active(self):
        """Check if notice is currently active"""
        now = timezone.now()
        if self.status != 'published':
            return False
        if self.valid_until and now > self.valid_until:
            return False
        return now >= self.valid_from

    @property
    def total_recipients(self):
        """Get total number of recipients"""
        return self.recipients.count()

    @property
    def read_count(self):
        """Get number of recipients who have read the notice"""
        return self.recipients.filter(is_read=True).count()

    @property
    def unread_count(self):
        """Get number of recipients who haven't read the notice"""
        return self.recipients.filter(is_read=False).count()


class NoticeRecipient(models.Model):
    """
    Model to track individual recipients of notices and their read status
    """
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Read status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Delivery status
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    sms_sent = models.BooleanField(default=False)
    sms_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['notice', 'user']
        ordering = ['-created_at']
        verbose_name = 'Notice Recipient'
        verbose_name_plural = 'Notice Recipients'

    def __str__(self):
        return f"{self.notice.title} - {self.user.get_full_name() or self.user.username}"

    def mark_as_read(self):
        """Mark notice as read by this recipient"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class NoticeCategory(models.Model):
    """
    Model for categorizing notices
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff',
                           help_text="Hex color code for category display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']
        verbose_name = 'Notice Category'
        verbose_name_plural = 'Notice Categories'

    def __str__(self):
        return self.name



