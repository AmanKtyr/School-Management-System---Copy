from django.contrib import admin
from .models import (
    ExamType, Exam, ExamSchedule, QuestionPaper, Room, SeatAllocation,
    InvigilatorAssignment, AdmitCard, ExamAttendance, AnswerSheet,
    GradeSystem, Mark
)

# Register your models here.
@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'exam_type', 'session', 'term', 'start_date', 'end_date', 'status')
    list_filter = ('exam_type', 'session', 'term', 'status')
    search_fields = ('name',)

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'student_class', 'section', 'date', 'start_time', 'end_time')
    list_filter = ('exam', 'student_class', 'date')
    search_fields = ('subject__name', 'student_class__name')

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('exam', 'subject', 'student_class', 'section', 'total_marks', 'passing_marks', 'generation_type')
    list_filter = ('exam', 'student_class', 'generation_type')
    search_fields = ('subject__name', 'student_class__name')

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'location')
    search_fields = ('name', 'location')

@admin.register(SeatAllocation)
class SeatAllocationAdmin(admin.ModelAdmin):
    list_display = ('exam', 'exam_schedule', 'room', 'student', 'seat_number', 'row_number', 'column_number')
    list_filter = ('exam', 'room')
    search_fields = ('student__fullname', 'seat_number')

@admin.register(InvigilatorAssignment)
class InvigilatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('exam', 'exam_schedule', 'room', 'staff', 'is_chief_invigilator')
    list_filter = ('exam', 'room', 'is_chief_invigilator')
    search_fields = ('staff__fullname',)

@admin.register(AdmitCard)
class AdmitCardAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'roll_number', 'generated_on', 'is_printed')
    list_filter = ('exam', 'is_printed')
    search_fields = ('student__fullname', 'roll_number')

@admin.register(ExamAttendance)
class ExamAttendanceAdmin(admin.ModelAdmin):
    list_display = ('exam_schedule', 'student', 'status', 'marked_by', 'marked_at')
    list_filter = ('exam_schedule__exam', 'status')
    search_fields = ('student__fullname',)

@admin.register(AnswerSheet)
class AnswerSheetAdmin(admin.ModelAdmin):
    list_display = ('exam_schedule', 'student', 'status', 'assigned_to', 'evaluated_by', 'evaluated_at')
    list_filter = ('exam_schedule__exam', 'status')
    search_fields = ('student__fullname',)

@admin.register(GradeSystem)
class GradeSystemAdmin(admin.ModelAdmin):
    list_display = ('grade', 'min_marks', 'max_marks', 'grade_point', 'description')
    list_filter = ('grade',)
    search_fields = ('grade', 'description')

@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('exam', 'exam_schedule', 'student', 'marks_obtained', 'is_pass', 'grade', 'status')
    list_filter = ('exam', 'is_pass', 'grade', 'status')
    search_fields = ('student__fullname',)
