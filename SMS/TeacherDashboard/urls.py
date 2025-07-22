from django.urls import path, include
from .views import (
    # Original views
    teacher_dashboard,
    teacher_students_list,
    teacher_attendance_list,
    teacher_exams_list,
    teacher_documents_list,
    teacher_profile,
    teacher_attendance_mark,
    teacher_marks_entry,
    teacher_student_detail,

    # Enhanced Student Management Views
    TeacherStudentListView,
    TeacherStudentDetailView,
    TeacherStudentCreateView,
    TeacherStudentUpdateView,
    TeacherStudentDeleteView,
    TeacherStudentBulkUploadView,
    TeacherStudentUDISECreateView,
    TeacherStudentUDISEUpdateView,
    teacher_download_csv,
    teacher_upload_student_documents,
    teacher_create_udise_info,
    teacher_get_sections_for_class,

    # Enhanced Attendance Management Views
    teacher_attendance_management,
    teacher_get_students_for_attendance,
    teacher_submit_attendance,
    teacher_attendance_reports,
)

urlpatterns = [
    # Main Dashboard
    path('dashboard/', teacher_dashboard, name='teacher_dashboard'),

    # Test URL to verify teacher dashboard is working
    path('test/', lambda request: HttpResponse("TEACHER DASHBOARD IS WORKING!"), name='teacher_test'),

    # ============ COMPREHENSIVE STUDENT MANAGEMENT ============
    # Enhanced Student Management (Class-based views)
    path('students/list/', TeacherStudentListView.as_view(), name='teacher_students_list'),
    path('students/<int:pk>/', TeacherStudentDetailView.as_view(), name='teacher_student_detail'),
    path('students/create/', TeacherStudentCreateView.as_view(), name='teacher_student_create'),
    path('students/<int:pk>/update/', TeacherStudentUpdateView.as_view(), name='teacher_student_update'),
    path('students/delete/<int:pk>/', TeacherStudentDeleteView.as_view(), name='teacher_student_delete'),
    path('students/upload/', TeacherStudentBulkUploadView.as_view(), name='teacher_student_upload'),
    path('students/download-csv/', teacher_download_csv, name='teacher_download_csv'),
    path('students/<int:pk>/upload-documents/', teacher_upload_student_documents, name='teacher_upload_student_documents'),

    # UDISE+ style forms
    path('students/create-udise/', TeacherStudentUDISECreateView.as_view(), name='teacher_student_create_udise'),
    path('students/<int:pk>/update-udise/', TeacherStudentUDISEUpdateView.as_view(), name='teacher_student_update_udise'),
    path('students/<int:pk>/create-udise-info/', teacher_create_udise_info, name='teacher_create_udise_info'),

    # API endpoints for students
    path('students/api/class/<int:class_id>/sections/', teacher_get_sections_for_class, name='teacher_get_sections_for_class'),

    # ============ COMPREHENSIVE ATTENDANCE MANAGEMENT ============
    # Enhanced Attendance Management
    path('attendance/list/', teacher_attendance_list, name='attendance_list'),
    path('attendance/get-students/<int:class_id>/', teacher_get_students_for_attendance, name='attendance_get_students'),

    # ============ ORIGINAL VIEWS (Backward Compatibility) ============
    # Original Students Management (Function-based views - kept for backward compatibility)
    path('students/', teacher_students_list, name='teacher_students_list_old'),
    path('students/detail/<int:pk>/', teacher_student_detail, name='teacher_student_detail_old'),

    # Original Attendance Management (Function-based views - kept for backward compatibility)
    path('attendance/', teacher_attendance_list, name='teacher_attendance_list'),
    path('attendance/mark/', teacher_attendance_mark, name='teacher_attendance_mark'),

    # ============ OTHER FEATURES ============
    # Examinations (Teacher-specific)
    path('exams/', teacher_exams_list, name='teacher_exams_list'),
    path('exams/marks-entry/', teacher_marks_entry, name='teacher_marks_entry'),

    # Documents (Teacher-specific)
    path('documents/', teacher_documents_list, name='teacher_documents_list'),

    # Profile
    path('profile/', teacher_profile, name='teacher_profile'),
]
