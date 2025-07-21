from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from apps.students.models import Student
from apps.staffs.models import Staff
from apps.attendance.models import Attendance
from apps.exams.models import Exam, Mark
from apps.documents.models import Document


@login_required
def teacher_dashboard(request):
    """Main teacher dashboard"""
    try:
        # Get the staff object for the logged-in user
        staff = Staff.objects.get(user=request.user)

        # Get teacher's assigned classes/students (you may need to adjust this based on your model structure)
        teacher_students = Student.objects.filter(current_status='active')[:10]  # Limit for dashboard
        recent_exams = Exam.objects.all()[:5]

        context = {
            'staff': staff,
            'teacher_students': teacher_students,
            'recent_exams': recent_exams,
            'total_students': teacher_students.count(),
        }
        return render(request, 'TeacherDashboard/dashboard.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found. Please contact administrator.')
        return render(request, 'TeacherDashboard/dashboard.html', {})


@login_required
def teacher_students_list(request):
    """Teacher-specific student list"""
    try:
        staff = Staff.objects.get(user=request.user)
        # Get students assigned to this teacher (adjust query as needed)
        students = Student.objects.filter(current_status='active')

        context = {
            'students': students,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/students_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/students_list.html', {})


@login_required
def teacher_student_detail(request, pk):
    """Teacher-specific student detail view"""
    student = get_object_or_404(Student, pk=pk)
    try:
        staff = Staff.objects.get(user=request.user)
        context = {
            'student': student,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/student_detail.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/student_detail.html', {'student': student})


@login_required
def teacher_attendance_list(request):
    """Teacher-specific attendance management"""
    try:
        staff = Staff.objects.get(user=request.user)
        # Get attendance records for teacher's classes
        attendance_records = Attendance.objects.all()[:20]  # Adjust query as needed

        context = {
            'attendance_records': attendance_records,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/attendance_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/attendance_list.html', {})


@login_required
def teacher_attendance_mark(request):
    """Teacher attendance marking interface"""
    try:
        staff = Staff.objects.get(user=request.user)
        students = Student.objects.filter(current_status='active')

        context = {
            'students': students,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/attendance_mark.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/attendance_mark.html', {})


@login_required
def teacher_exams_list(request):
    """Teacher-specific exams list"""
    try:
        staff = Staff.objects.get(user=request.user)
        exams = Exam.objects.all()

        context = {
            'exams': exams,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/exams_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/exams_list.html', {})


@login_required
def teacher_marks_entry(request):
    """Teacher marks entry interface"""
    try:
        staff = Staff.objects.get(user=request.user)
        exams = Exam.objects.all()
        students = Student.objects.filter(current_status='active')

        context = {
            'exams': exams,
            'students': students,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/marks_entry.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/marks_entry.html', {})


@login_required
def teacher_documents_list(request):
    """Teacher-specific documents"""
    try:
        staff = Staff.objects.get(user=request.user)
        documents = Document.objects.all()[:20]  # Adjust query as needed

        context = {
            'documents': documents,
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/documents_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/documents_list.html', {})


@login_required
def teacher_profile(request):
    """Teacher profile management"""
    try:
        staff = Staff.objects.get(user=request.user)

        context = {
            'staff': staff,
        }
        return render(request, 'TeacherDashboard/profile.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/profile.html', {})
