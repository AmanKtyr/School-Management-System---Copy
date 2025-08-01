from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, DateTimeInput
from .models import Notice, NoticeCategory
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.corecode.models import StudentClass


class NoticeForm(ModelForm):
    """Form for creating and editing notices"""
    
    # Additional fields for recipient selection
    individual_recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select individual users (only shown when 'Individual Users' is selected as recipient type)"
    )
    
    class Meta:
        model = Notice
        fields = [
            'title', 'content', 'category', 'priority', 'status',
            'recipient_type', 'target_class', 'individual_recipients',
            'valid_from', 'valid_until', 'send_email', 'send_sms',
            'is_important', 'attachment'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notice title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter notice content'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'recipient_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_recipient_type'
            }),
            'target_class': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_target_class'
            }),
            'valid_from': DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'valid_until': DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'send_email': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'send_sms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_important': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter active categories
        self.fields['category'].queryset = NoticeCategory.objects.filter(is_active=True)
        
        # Filter active classes
        self.fields['target_class'].queryset = StudentClass.objects.all()
        
        # Set up individual recipients queryset with better display
        self.fields['individual_recipients'].queryset = User.objects.filter(
            is_active=True
        ).select_related().order_by('first_name', 'last_name', 'username')
        
        # Add empty option for optional fields
        self.fields['category'].empty_label = "Select Category (Optional)"
        self.fields['target_class'].empty_label = "Select Class"
        
        # Make some fields required based on recipient type
        if self.instance and self.instance.pk:
            if self.instance.recipient_type == 'class':
                self.fields['target_class'].required = True
            elif self.instance.recipient_type == 'individual':
                self.fields['individual_recipients'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        recipient_type = cleaned_data.get('recipient_type')
        target_class = cleaned_data.get('target_class')
        individual_recipients = cleaned_data.get('individual_recipients')
        
        # Validate recipient type specific requirements
        if recipient_type == 'class' and not target_class:
            raise forms.ValidationError("Please select a target class when recipient type is 'Specific Class'.")
        
        if recipient_type == 'individual' and not individual_recipients:
            raise forms.ValidationError("Please select at least one individual recipient when recipient type is 'Individual Users'.")
        
        # Validate date range
        valid_from = cleaned_data.get('valid_from')
        valid_until = cleaned_data.get('valid_until')
        
        if valid_from and valid_until and valid_until <= valid_from:
            raise forms.ValidationError("Valid until date must be after valid from date.")
        
        return cleaned_data


class NoticeCategoryForm(ModelForm):
    """Form for creating and editing notice categories"""
    
    class Meta:
        model = NoticeCategory
        fields = ['name', 'description', 'color', 'is_active']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class NoticeFilterForm(forms.Form):
    """Form for filtering notices"""
    
    PRIORITY_CHOICES = [('', 'All Priorities')] + Notice.PRIORITY_CHOICES
    STATUS_CHOICES = [('', 'All Status')] + Notice.STATUS_CHOICES
    RECIPIENT_TYPE_CHOICES = [('', 'All Types')] + Notice.RECIPIENT_TYPE_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search notices...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=NoticeCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    recipient_type = forms.ChoiceField(
        choices=RECIPIENT_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    created_by = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label="All Creators",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_important = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class QuickNoticeForm(forms.Form):
    """Simplified form for quick notice creation"""
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter notice title'
        })
    )
    
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter notice content'
        })
    )
    
    recipient_type = forms.ChoiceField(
        choices=Notice.RECIPIENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=Notice.PRIORITY_CHOICES,
        initial='medium',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_important = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
