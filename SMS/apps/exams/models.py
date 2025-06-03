from django.db import models
from django.urls import reverse
from django.utils import timezone
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from apps.staffs.models import Staff

# Create your models here.

class ExamType(models.Model):
    """Model for different types of exams (unit test, mid-term, final, etc.)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    """Main exam model with details"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} - {self.session} {self.term}"

    def get_absolute_url(self):
        return reverse('exams:exam_detail', kwargs={'pk': self.pk})

class ExamSchedule(models.Model):
    """Model for exam timetables"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    section = models.CharField(max_length=10, blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    venue = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['exam', 'subject', 'student_class', 'section', 'date']

    def __str__(self):
        return f"{self.subject} - {self.student_class} {self.section or ''} - {self.date}"

class QuestionPaper(models.Model):
    """Model for managing question papers"""
    GENERATION_CHOICES = [
        ('auto', 'Auto-Generated'),
        ('manual', 'Manually Uploaded'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    section = models.CharField(max_length=10, blank=True, null=True)
    total_marks = models.PositiveIntegerField()
    passing_marks = models.PositiveIntegerField()
    generation_type = models.CharField(max_length=10, choices=GENERATION_CHOICES, default='manual')
    file = models.FileField(upload_to='exams/question_papers/', blank=True, null=True)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.student_class} {self.section or ''} - {self.exam.name}"

class Room(models.Model):
    """Model for managing exam rooms"""
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class SeatAllocation(models.Model):
    """Model for student seating arrangements"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=20)
    row_number = models.PositiveIntegerField()
    column_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam_schedule', 'room', 'seat_number']

    def __str__(self):
        return f"{self.student.fullname} - {self.room.name} - Seat {self.seat_number}"

class InvigilatorAssignment(models.Model):
    """Model for assigning teachers to exams"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    is_chief_invigilator = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['exam_schedule', 'room', 'staff']

    def __str__(self):
        return f"{self.staff.fullname} - {self.room.name} - {self.exam_schedule}"

class AdmitCard(models.Model):
    """Model for generating student admit cards"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=50)
    generated_on = models.DateTimeField(auto_now_add=True)
    is_printed = models.BooleanField(default=False)
    printed_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['exam', 'student']

    def __str__(self):
        return f"{self.student.fullname} - {self.exam.name}"

class ExamAttendance(models.Model):
    """Model for tracking student attendance in exams"""
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=ATTENDANCE_CHOICES, default='absent')
    remarks = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['exam_schedule', 'student']

    def __str__(self):
        return f"{self.student.fullname} - {self.exam_schedule} - {self.get_status_display()}"

class AnswerSheet(models.Model):
    """Model for uploading and evaluating answer sheets"""
    STATUS_CHOICES = [
        ('pending', 'Pending Evaluation'),
        ('evaluating', 'Under Evaluation'),
        ('completed', 'Evaluation Completed'),
    ]

    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='exams/answer_sheets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_answer_sheets')
    evaluated_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluated_answer_sheets')
    evaluated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['exam_schedule', 'student']

    def __str__(self):
        return f"{self.student.fullname} - {self.exam_schedule.subject}"

class GradeSystem(models.Model):
    """Model for defining grade boundaries"""
    name = models.CharField(max_length=100)
    min_marks = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=5)
    grade_point = models.DecimalField(max_digits=3, decimal_places=1)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-min_marks']

    def __str__(self):
        return f"{self.grade} ({self.min_marks}-{self.max_marks})"

class Mark(models.Model):
    """Model for recording student marks and generating results"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('finalized', 'Finalized'),
        ('published', 'Published'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    is_pass = models.BooleanField(default=False)
    grade = models.CharField(max_length=5, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    entered_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='entered_marks')
    verified_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_marks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['exam_schedule', 'student']

    def __str__(self):
        return f"{self.student.fullname} - {self.exam_schedule.subject} - {self.marks_obtained}"

    def save(self, *args, **kwargs):
        # Auto-calculate if the student passed based on question paper passing marks
        question_paper = QuestionPaper.objects.filter(
            exam=self.exam,
            subject=self.exam_schedule.subject,
            student_class=self.student.current_class
        ).first()

        if question_paper and self.marks_obtained >= question_paper.passing_marks:
            self.is_pass = True
        else:
            self.is_pass = False

        # Auto-assign grade based on grade system
        grade_info = GradeSystem.objects.filter(
            min_marks__lte=self.marks_obtained,
            max_marks__gte=self.marks_obtained
        ).first()

        if grade_info:
            self.grade = grade_info.grade

        super().save(*args, **kwargs)
