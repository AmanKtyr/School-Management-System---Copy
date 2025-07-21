from django.urls import path, include
from .views import (
    teacher_dashboard,
    teacher_students_list,
    teacher_attendance_list,
    teacher_exams_list,
    teacher_documents_list,
    teacher_profile,
    teacher_attendance_mark,
    teacher_marks_entry,
    teacher_student_detail,
)

urlpatterns = [
    # Main Dashboard
    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),

    # Students Management (Teacher-specific)
    path('students/', teacher_students_list, name='teacher_students_list'),
    path('students/<int:pk>/', teacher_student_detail, name='teacher_student_detail'),

    # Attendance Management (Teacher-specific)
    path('attendance/', teacher_attendance_list, name='teacher_attendance_list'),
    path('attendance/mark/', teacher_attendance_mark, name='teacher_attendance_mark'),

    # Examinations (Teacher-specific)
    path('exams/', teacher_exams_list, name='teacher_exams_list'),
    path('exams/marks-entry/', teacher_marks_entry, name='teacher_marks_entry'),

    # Documents (Teacher-specific)
    path('documents/', teacher_documents_list, name='teacher_documents_list'),

    # Profile
    path('profile/', teacher_profile, name='teacher_profile'),
]
