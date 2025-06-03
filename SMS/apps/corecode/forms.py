from django import forms
from django.forms import ModelForm, modelformset_factory

from .models import (
    AcademicSession,
    AcademicTerm,
    SiteConfig,
    StudentClass,
    Subject,
    CollegeProfile,
)

class SiteConfigForm(forms.ModelForm):
    class Meta:
        model = SiteConfig
        fields = ['key', 'value']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
        }

# Create a formset for SiteConfig
SiteConfigFormSet = modelformset_factory(
    SiteConfig,
    form=SiteConfigForm,
    extra=0,  # No extra empty forms
    can_delete=False  # Prevent deletion of configurations
)

class AcademicSessionForm(ModelForm):
    prefix = "Academic Session"

    class Meta:
        model = AcademicSession
        fields = ["name", "current"]


class AcademicTermForm(ModelForm):
    prefix = "Academic Term"

    class Meta:
        model = AcademicTerm
        fields = ["name", "current"]


class SubjectForm(ModelForm):
    prefix = "Subject"

    class Meta:
        model = Subject
        fields = ["name"]


class StudentClassForm(ModelForm):
    prefix = "Class"

    class Meta:
        model = StudentClass
        fields = ["name"]


class CurrentSessionForm(forms.Form):
    current_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        help_text='Click <a href="/session/create/?next=current-session/">here</a> to add new session',
    )
    current_term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        help_text='Click <a href="/term/create/?next=current-session/">here</a> to add new term',
    )

class CollegeProfileForm(forms.ModelForm):
    class Meta:
        model = CollegeProfile
        fields = [
            'college_name', 'college_address', 'college_email', 'college_phone',
            'college_logo', 'established_year', 'principal_name', 'college_type',
            'admin_email', 'admin_contact', 'facebook_link', 'twitter_link', 'linkedin_link'
        ]
        widgets = {
            'college_address': forms.Textarea(attrs={'rows': 3}),
        }
