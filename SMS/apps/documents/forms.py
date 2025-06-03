from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms import modelformset_factory

from apps.students.models import Student
from apps.staffs.models import Staff
from apps.exams.models import Exam

from .models import (
    DocumentCategory, DocumentType, Document,
    StudentDocument, StaffDocument, ExamDocument,
    DocumentTemplate
)

class DocumentCategoryForm(forms.ModelForm):
    class Meta:
        model = DocumentCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ['name', 'entity_type', 'category', 'description', 'required', 'template']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'title', 'document_type', 'file', 'document_number',
            'status', 'description', 'tags', 'expiry_date'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentDocumentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(current_status='active'),
        empty_label="Select Student"
    )
    
    class Meta:
        model = StudentDocument
        fields = ['student', 'document']

class StaffDocumentForm(forms.ModelForm):
    staff = forms.ModelChoiceField(
        queryset=Staff.objects.filter(current_status='active'),
        empty_label="Select Staff"
    )
    
    class Meta:
        model = StaffDocument
        fields = ['staff', 'document']

class ExamDocumentForm(forms.ModelForm):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        empty_label="Select Exam"
    )
    
    class Meta:
        model = ExamDocument
        fields = ['exam', 'document']

class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = ['name', 'description', 'file', 'document_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DocumentUploadForm(forms.Form):
    """Form for uploading documents with entity selection"""
    ENTITY_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('exam', 'Exam'),
        ('general', 'General'),
    ]
    
    entity_type = forms.ChoiceField(choices=ENTITY_CHOICES, required=True)
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        empty_label="Select Document Type",
        required=True
    )
    title = forms.CharField(max_length=200, required=True)
    file = forms.FileField(required=True)
    document_number = forms.CharField(max_length=50, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    tags = forms.CharField(max_length=200, required=False, help_text='Comma-separated tags')
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    
    # These fields will be populated dynamically based on entity_type
    student = forms.ModelChoiceField(
        queryset=Student.objects.filter(current_status='active'),
        empty_label="Select Student",
        required=False
    )
    
    staff = forms.ModelChoiceField(
        queryset=Staff.objects.filter(current_status='active'),
        empty_label="Select Staff",
        required=False
    )
    
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        empty_label="Select Exam",
        required=False
    )

class DocumentSearchForm(forms.Form):
    """Form for searching documents"""
    ENTITY_CHOICES = [
        ('', 'All'),
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('exam', 'Exam'),
        ('general', 'General'),
    ]
    
    STATUS_CHOICES = [
        ('', 'All'),
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    search_query = forms.CharField(max_length=100, required=False, label="Search")
    entity_type = forms.ChoiceField(choices=ENTITY_CHOICES, required=False, label="Entity Type")
    document_type = forms.ModelChoiceField(
        queryset=DocumentType.objects.all(),
        empty_label="All Document Types",
        required=False,
        label="Document Type"
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label="Status")
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="From Date"
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label="To Date"
    )
