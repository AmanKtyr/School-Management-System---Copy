from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from apps.students.models import Student
from apps.staffs.models import Staff
from apps.exams.models import Exam

# Create your models here.

class DocumentCategory(models.Model):
    """Model for document categories"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Document Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class DocumentType(models.Model):
    """Model for document types"""
    ENTITY_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('exam', 'Exam'),
        ('general', 'General'),
    ]

    name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES, default='general')
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, related_name='document_types')
    description = models.TextField(blank=True, null=True)
    required = models.BooleanField(default=False)
    template = models.FileField(upload_to='documents/templates/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

class Document(models.Model):
    """Main document model"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    title = models.CharField(max_length=200)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/files/')
    document_number = models.CharField(max_length=50, blank=True, null=True)

    # Generic relation to connect to different models (Student, Staff, Exam)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    version = models.PositiveIntegerField(default=1)
    is_latest = models.BooleanField(default=True)

    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True, help_text='Comma-separated tags')

    created_by = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('documents:document_detail', kwargs={'pk': self.pk})

    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    def save(self, *args, **kwargs):
        # Check if document is expired
        if self.is_expired():
            self.status = 'expired'

        super().save(*args, **kwargs)

class StudentDocument(models.Model):
    """Model for student-specific documents"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_documents')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='student_documents')

    def __str__(self):
        return f"{self.document.title} - {self.student.fullname}"

class StaffDocument(models.Model):
    """Model for staff-specific documents"""
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='staff_documents')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='staff_documents')

    def __str__(self):
        return f"{self.document.title} - {self.staff.fullname}"

class ExamDocument(models.Model):
    """Model for exam-specific documents"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='exam_documents')
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='exam_documents')

    def __str__(self):
        return f"{self.document.title} - {self.exam.name}"

class DocumentTemplate(models.Model):
    """Model for document templates"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/templates/')
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
