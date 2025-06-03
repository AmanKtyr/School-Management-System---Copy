from django import forms
from .models import StudentClass
from apps.students.models import Student

class ClassSectionFilterForm(forms.Form):
    class_name = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=False,
        empty_label="-- All Classes--",
        label="Select Class",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'class-filter'
        }),
    )

    section = forms.ChoiceField(
        choices=[],
        required=False,
        label="Select Section",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'section-filter'
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize with just the default option
        self.fields['section'].choices = [('', '-- All Sections --')]

        # If a class is selected, get sections for that class
        if args and args[0] and 'class_name' in args[0] and args[0]['class_name']:
            class_id = args[0]['class_name']
            sections = Student.objects.filter(
                current_class_id=class_id,
                current_status='active'
            ).values_list('section', flat=True).distinct()

            section_choices = [('', '-- All Sections --')] + [(section, section) for section in sections if section]
            self.fields['section'].choices = section_choices
