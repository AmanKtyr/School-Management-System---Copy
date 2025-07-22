from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from .models import Student
from apps.corecode.models import Section

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [f.name for f in Student._meta.fields if f.name != 'registration_number']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add date pickers and other widget customizations
        self.fields["aadhar"].widget = widgets.TextInput(attrs={"row": 2})
        self.fields["date_of_birth"].widget = widgets.DateInput(attrs={"type": "date"})
        self.fields["date_of_admission"].widget = widgets.DateInput(attrs={"type": "date"})
        self.fields["address"].widget = widgets.Textarea(attrs={"rows": 2})
        self.fields["others"].widget = widgets.Textarea(attrs={"rows": 2})
        
        # Make section a select field that depends on the current_class
        self.fields['section'].widget = forms.Select(attrs={'class': 'form-select'})
        self.fields['section'].choices = [('', '-- Select Section --')]
        
        # If we're editing an existing student, populate the section choices
        if self.instance and self.instance.pk and self.instance.current_class:
            # Get sections from the Section model
            sections = Section.objects.filter(
                student_class=self.instance.current_class,
                is_active=True
            ).values_list('name', flat=True)
            
            # Add the sections to the choices
            self.fields['section'].choices += [(section, section) for section in sections]
            
            # If the current section isn't in the list (might be from before we had the Section model)
            # add it to the choices
            if self.instance.section and self.instance.section not in sections:
                self.fields['section'].choices += [(self.instance.section, self.instance.section)]

    def clean(self):
        """Additional form validation"""
        cleaned_data = super().clean()

        # Validate that required fields are present
        current_class = cleaned_data.get('current_class')
        fullname = cleaned_data.get('fullname')
        date_of_admission = cleaned_data.get('date_of_admission')

        if not fullname:
            raise ValidationError("Student name is required.")

        if not current_class:
            raise ValidationError("Please select a class for the student.")

        if not date_of_admission:
            raise ValidationError("Date of admission is required.")

        # Additional validation for mobile numbers
        mobile_number = cleaned_data.get('mobile_number')
        father_mobile = cleaned_data.get('Father_mobile_number')

        if mobile_number and father_mobile and mobile_number == father_mobile:
            raise ValidationError("Student mobile number and father's mobile number cannot be the same.")

        return cleaned_data
