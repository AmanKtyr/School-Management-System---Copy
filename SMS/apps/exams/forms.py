from django import forms
from django.forms import modelformset_factory
from .models import (
    ExamType, Exam, ExamSchedule, QuestionPaper, Room, SeatAllocation,
    InvigilatorAssignment, AdmitCard, ExamAttendance, AnswerSheet,
    GradeSystem, Mark
)
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from apps.staffs.models import Staff

class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'exam_type', 'session', 'term', 'start_date', 'end_date', 'status', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ExamScheduleForm(forms.ModelForm):
    class Meta:
        model = ExamSchedule
        fields = ['exam', 'subject', 'student_class', 'section', 'date', 'start_time', 'end_time', 'duration_minutes', 'venue']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class QuestionPaperForm(forms.ModelForm):
    class Meta:
        model = QuestionPaper
        fields = ['exam', 'subject', 'student_class', 'section', 'total_marks', 'passing_marks', 'generation_type', 'file']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'capacity', 'location', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SeatAllocationForm(forms.ModelForm):
    class Meta:
        model = SeatAllocation
        fields = ['exam', 'exam_schedule', 'room', 'student', 'seat_number', 'row_number', 'column_number']

class InvigilatorAssignmentForm(forms.ModelForm):
    class Meta:
        model = InvigilatorAssignment
        fields = ['exam', 'exam_schedule', 'room', 'staff', 'is_chief_invigilator']

class AdmitCardForm(forms.ModelForm):
    class Meta:
        model = AdmitCard
        fields = ['exam', 'student', 'roll_number']

class ExamAttendanceForm(forms.ModelForm):
    class Meta:
        model = ExamAttendance
        fields = ['exam_schedule', 'student', 'status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

class AnswerSheetForm(forms.ModelForm):
    class Meta:
        model = AnswerSheet
        fields = ['exam_schedule', 'student', 'file', 'status', 'assigned_to']

class GradeSystemForm(forms.ModelForm):
    class Meta:
        model = GradeSystem
        fields = ['name', 'min_marks', 'max_marks', 'grade', 'grade_point', 'description']

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['exam', 'exam_schedule', 'student', 'marks_obtained', 'remarks', 'status']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }

# Formsets for bulk operations
ExamScheduleFormSet = modelformset_factory(
    ExamSchedule,
    form=ExamScheduleForm,
    extra=1,
    can_delete=True
)

SeatAllocationFormSet = modelformset_factory(
    SeatAllocation,
    form=SeatAllocationForm,
    extra=1,
    can_delete=True
)

InvigilatorAssignmentFormSet = modelformset_factory(
    InvigilatorAssignment,
    form=InvigilatorAssignmentForm,
    extra=1,
    can_delete=True
)

ExamAttendanceFormSet = modelformset_factory(
    ExamAttendance,
    form=ExamAttendanceForm,
    extra=0,
    can_delete=False
)

MarkFormSet = modelformset_factory(
    Mark,
    form=MarkForm,
    extra=0,
    can_delete=False,
    fields=['marks_obtained', 'remarks']
)

# Filter forms
class ExamFilterForm(forms.Form):
    session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        required=False,
        empty_label="-- All Sessions --"
    )
    term = forms.ModelChoiceField(
        queryset=AcademicTerm.objects.all(),
        required=False,
        empty_label="-- All Terms --"
    )
    exam_type = forms.ModelChoiceField(
        queryset=ExamType.objects.all(),
        required=False,
        empty_label="-- All Exam Types --"
    )
    status = forms.ChoiceField(
        choices=[('', '-- All Statuses --')] + list(Exam.STATUS_CHOICES),
        required=False
    )

class ExamScheduleFilterForm(forms.Form):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.all(),
        required=False,
        empty_label="-- All Exams --"
    )
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=False,
        empty_label="-- All Classes --"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        empty_label="-- All Subjects --"
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

class StudentExamFilterForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        empty_label="-- All Students --"
    )
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        required=False,
        empty_label="-- All Classes --"
    )
    section = forms.CharField(
        required=False,
        max_length=10
    )
