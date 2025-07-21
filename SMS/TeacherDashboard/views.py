import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction
from django.utils import timezone
import datetime

from apps.students.models import Student, StudentBulkUpload, StudentDocument, StudentUDISEInfo
from apps.students.forms import StudentForm
from apps.staffs.models import Staff
from apps.attendance.models import Attendance, Holiday
from apps.exams.models import Exam, Mark
from apps.documents.models import Document
from apps.corecode.models import StudentClass, Section
from apps.corecode.filters import ClassSectionFilterForm


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
        return render(request, 'TeacherDashboard/students/students_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/students/students_list.html', {})


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
        return render(request, 'TeacherDashboard/students/student_detail.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/students/student_detail.html', {'student': student})


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
        return render(request, 'TeacherDashboard/attendance/attendance_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/attendance/attendance_list.html', {})


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
        return render(request, 'TeacherDashboard/attendance/attendance_mark.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/attendance/attendance_mark.html', {})


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
        return render(request, 'TeacherDashboard/exams/exams_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/exams/exams_list.html', {})


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
        return render(request, 'TeacherDashboard/marks/marks_entry.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/marks/marks_entry.html', {})


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
        return render(request, 'TeacherDashboard/documents/documents_list.html', context)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff profile not found.')
        return render(request, 'TeacherDashboard/documents/documents_list.html', {})


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


# ============ COMPREHENSIVE STUDENT MANAGEMENT VIEWS ============

class TeacherStudentListView(LoginRequiredMixin, ListView):
    """Enhanced student list view for teachers with filtering"""
    model = Student
    template_name = "TeacherDashboard/students/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = ClassSectionFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            if self.filter_form.cleaned_data['class_name']:
                queryset = queryset.filter(current_class=self.filter_form.cleaned_data['class_name'])
            if self.filter_form.cleaned_data['section']:
                queryset = queryset.filter(section=self.filter_form.cleaned_data['section'])

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None
        return context


class TeacherStudentDetailView(LoginRequiredMixin, DetailView):
    """Enhanced student detail view for teachers"""
    model = Student
    template_name = "TeacherDashboard/students/student_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None

        # Get student documents if they exist
        context['documents'] = StudentDocument.objects.filter(student=self.object).first()

        # Get UDISE information if it exists
        try:
            context['udise_info'] = StudentUDISEInfo.objects.get(student=self.object)
        except (StudentUDISEInfo.DoesNotExist, Exception) as e:
            context['udise_info'] = None
            if not isinstance(e, StudentUDISEInfo.DoesNotExist):
                context['needs_migration'] = True

        # Get pending fees
        from apps.fees.models import PendingFee, FeePayment
        from django.db.models import Sum

        # Get all pending fees that are not paid
        pending_fees = PendingFee.objects.filter(student=self.object, paid=False).order_by('due_date')
        context['pending_fees'] = pending_fees

        # Calculate total pending amount
        total_pending = sum(fee.get_discounted_amount() for fee in pending_fees)
        context['total_pending_amount'] = total_pending

        # Get payment history
        payment_history = FeePayment.objects.filter(student=self.object).order_by('-date')[:5]
        context['payment_history'] = payment_history

        # Calculate total paid amount
        total_paid = FeePayment.objects.filter(student=self.object, status='Paid').aggregate(total=Sum('amount'))['total'] or 0
        context['total_paid_amount'] = total_paid

        return context


class TeacherStudentCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Student creation view for teachers"""
    model = Student
    form_class = StudentForm
    template_name = "TeacherDashboard/students/student_form.html"
    success_message = "New student successfully added."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add AJAX functionality to update sections when class changes
        form.fields['current_class'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'loadSections(this.value)'
        })

        return form

    def form_valid(self, form):
        from django.db import IntegrityError
        from django.contrib import messages

        try:
            return super().form_valid(form)
        except IntegrityError as e:
            if 'registration_number' in str(e):
                messages.error(
                    self.request,
                    "Registration number conflict occurred. Please try again. If the problem persists, contact the administrator."
                )
                return self.form_invalid(form)
            else:
                messages.error(
                    self.request,
                    f"Database error occurred: {str(e)}. Please check your data and try again."
                )
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('teacher_student_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None
        return context


class TeacherStudentUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Student update view for teachers"""
    model = Student
    form_class = StudentForm
    template_name = "TeacherDashboard/students/student_form.html"
    success_message = "Student record successfully updated."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add AJAX functionality to update sections when class changes
        form.fields['current_class'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'loadSections(this.value)'
        })

        return form

    def get_success_url(self):
        return reverse_lazy('teacher_student_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None
        return context


class TeacherStudentDeleteView(LoginRequiredMixin, View):
    """Student deletion view for teachers"""
    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk)

        # Import related models
        from apps.fees.models import FeePayment, PendingFee
        from apps.exams.models import AdmitCard, ExamAttendance, Mark

        # Count related records
        related_data = {
            'fee_payments': FeePayment.objects.filter(student=student).count(),
            'pending_fees': PendingFee.objects.filter(student=student).count(),
            'admit_cards': AdmitCard.objects.filter(student=student).count(),
            'exam_attendance': ExamAttendance.objects.filter(student=student).count(),
            'marks': Mark.objects.filter(student=student).count(),
            'attendance': Attendance.objects.filter(student=student).count(),
            'documents': StudentDocument.objects.filter(student=student).count(),
        }

        context = {
            'object': student,
            'related_data': related_data
        }

        try:
            context['staff'] = Staff.objects.get(user=request.user)
        except Staff.DoesNotExist:
            context['staff'] = None

        return render(request, 'TeacherDashboard/students/student_confirm_delete.html', context)

    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student_id = student.id
        student_name = student.fullname

        try:
            # Try to delete UDISE info first if it exists
            try:
                udise_info = StudentUDISEInfo.objects.get(student=student)
                udise_info.delete()
            except StudentUDISEInfo.DoesNotExist:
                pass

            # Use Django's ORM to delete related records first
            from apps.fees.models import FeePayment, PendingFee
            from apps.exams.models import AdmitCard, ExamAttendance, Mark

            # Delete fee-related records
            FeePayment.objects.filter(student=student).delete()
            PendingFee.objects.filter(student=student).delete()

            # Delete exam-related records
            Mark.objects.filter(student=student).delete()
            ExamAttendance.objects.filter(student=student).delete()
            AdmitCard.objects.filter(student=student).delete()

            # Delete attendance records
            Attendance.objects.filter(student=student).delete()

            # Delete student documents
            StudentDocument.objects.filter(student=student).delete()

            # Finally delete the student
            student.delete()

            messages.success(request, f"Student '{student_name}' and all related records have been successfully deleted.")
            return redirect('teacher_students_list')

        except Exception as e:
            messages.error(request, f"Error deleting student: {str(e)}")
            return redirect('teacher_student_detail', pk=student_id)


class TeacherStudentBulkUploadView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Bulk student upload view for teachers"""
    model = StudentBulkUpload
    template_name = "TeacherDashboard/students/students_upload.html"
    fields = ["csv_file"]
    success_url = reverse_lazy("teacher_students_list")
    success_message = "Successfully uploaded students"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None
        return context


@login_required
def teacher_download_csv(request):
    """Download CSV template for student bulk upload"""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student_template.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "registration_number",
        "fullname",
        "gender",
        "parent_number",
        "address",
        "current_class",
    ])

    return response


@login_required
def teacher_upload_student_documents(request, pk):
    """Upload student documents for teachers"""
    student = get_object_or_404(Student, pk=pk)

    # Get or create student document record
    student_doc, created = StudentDocument.objects.get_or_create(student=student)

    if request.method == 'POST':
        # Handle document numbers and file uploads

        # Aadhar Card
        if 'aadhar_card' in request.FILES:
            student_doc.aadhar_card = request.FILES.get('aadhar_card')
            if 'aadhar_card_number' in request.POST:
                student_doc.aadhar_card_number = request.POST.get('aadhar_card_number')

        # Parent Photo
        if 'parent_photo' in request.FILES:
            student_doc.parent_photo = request.FILES.get('parent_photo')
            if 'parent_photo_number' in request.POST:
                student_doc.parent_photo_number = request.POST.get('parent_photo_number')

        # Parent ID Proof
        if 'parent_id_proof' in request.FILES:
            student_doc.parent_id_proof = request.FILES.get('parent_id_proof')
            if 'parent_id_proof_number' in request.POST:
                student_doc.parent_id_proof_number = request.POST.get('parent_id_proof_number')

        # Previous Marksheet
        if 'previous_marksheet' in request.FILES:
            student_doc.previous_marksheet = request.FILES.get('previous_marksheet')
            if 'previous_marksheet_number' in request.POST:
                student_doc.previous_marksheet_number = request.POST.get('previous_marksheet_number')

        # Transfer Certificate
        if 'transfer_certificate' in request.FILES:
            student_doc.transfer_certificate = request.FILES.get('transfer_certificate')
            if 'transfer_certificate_number' in request.POST:
                student_doc.transfer_certificate_number = request.POST.get('transfer_certificate_number')

        # Character Certificate
        if 'character_certificate' in request.FILES:
            student_doc.character_certificate = request.FILES.get('character_certificate')
            if 'character_certificate_number' in request.POST:
                student_doc.character_certificate_number = request.POST.get('character_certificate_number')

        # Caste Certificate
        if 'caste_certificate' in request.FILES:
            student_doc.caste_certificate = request.FILES.get('caste_certificate')
            if 'caste_certificate_number' in request.POST:
                student_doc.caste_certificate_number = request.POST.get('caste_certificate_number')

        student_doc.save()
        messages.success(request, 'Documents uploaded successfully!')
        return redirect('teacher_student_detail', pk=pk)

    context = {
        'student': student,
        'student_doc': student_doc,
    }

    try:
        context['staff'] = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        context['staff'] = None

    return render(request, 'TeacherDashboard/students/upload_documents.html', context)


class TeacherStudentUDISECreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """UDISE+ style form for creating a new student - Teacher version"""
    model = Student
    form_class = StudentForm
    template_name = "TeacherDashboard/students/udise_student_form.html"
    success_message = "New student successfully added using UDISE+ format."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add AJAX functionality to update sections when class changes
        form.fields['current_class'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'loadSections(this.value)'
        })

        return form

    def form_valid(self, form):
        from django.db import IntegrityError
        from django.contrib import messages

        try:
            return super().form_valid(form)
        except IntegrityError as e:
            if 'registration_number' in str(e):
                messages.error(
                    self.request,
                    "Registration number conflict occurred. The system will automatically generate a unique number. Please try again."
                )
                return self.form_invalid(form)
            else:
                messages.error(
                    self.request,
                    f"Database error occurred: {str(e)}. Please check your data and try again."
                )
                return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('teacher_student_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None
        return context


class TeacherStudentUDISEUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """UDISE+ style form for updating an existing student - Teacher version"""
    model = Student
    form_class = StudentForm
    template_name = "TeacherDashboard/students/udise_student_form.html"
    success_message = "Student record successfully updated using UDISE+ format."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Add AJAX functionality to update sections when class changes
        form.fields['current_class'].widget.attrs.update({
            'class': 'form-select',
            'onchange': 'loadSections(this.value)'
        })

        return form

    def get_success_url(self):
        return reverse_lazy('teacher_student_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['staff'] = Staff.objects.get(user=self.request.user)
        except Staff.DoesNotExist:
            context['staff'] = None
        return context


@login_required
def teacher_create_udise_info(request, pk):
    """Create UDISE information for a student - Teacher version"""
    student = get_object_or_404(Student, pk=pk)

    # Check if UDISE info already exists
    try:
        udise_info = StudentUDISEInfo.objects.get(student=student)
        messages.info(request, 'UDISE information already exists for this student.')
        return redirect('teacher_student_detail', pk=pk)
    except StudentUDISEInfo.DoesNotExist:
        pass

    if request.method == 'POST':
        # Create UDISE info with basic data from student
        udise_info = StudentUDISEInfo.objects.create(
            student=student,
            # Add default values or get from form
            # You can expand this based on your UDISE form fields
        )
        messages.success(request, 'UDISE information created successfully!')
        return redirect('teacher_student_detail', pk=pk)

    context = {
        'student': student,
    }

    try:
        context['staff'] = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        context['staff'] = None

    return render(request, 'TeacherDashboard/students/create_udise_info.html', context)


@login_required
def teacher_get_sections_for_class(request, class_id):
    """API endpoint to get sections for a class - Teacher version"""
    try:
        sections = Student.objects.filter(
            current_class_id=class_id,
            current_status='active'
        ).values_list('section', flat=True).distinct()

        sections_list = [{'value': section, 'text': section} for section in sections if section]

        return JsonResponse({'sections': sections_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ============ COMPREHENSIVE ATTENDANCE MANAGEMENT VIEWS ============

@login_required
def teacher_attendance_management(request):
    """Enhanced attendance management for teachers"""
    classes = StudentClass.objects.all()
    selected_class_id = request.GET.get('class_id')
    selected_section = request.GET.get('section', '')

    # Get attendance date from request or use today's date
    attendance_date_str = request.GET.get('attendance_date')
    today = timezone.now().date()

    # Calculate one week ago for date restriction
    one_week_ago = today - datetime.timedelta(days=7)

    if attendance_date_str:
        try:
            attendance_date = datetime.datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
            # Ensure date is not in the future and not more than a week in the past
            if attendance_date > today:
                attendance_date = today
            elif attendance_date < one_week_ago:
                attendance_date = one_week_ago
        except ValueError:
            attendance_date = today
    else:
        attendance_date = today

    students = []
    selected_class_name = None
    sections = []
    weekly_attendance = []

    # Check if the selected date is a Sunday
    is_sunday = attendance_date.weekday() == 6  # 6 represents Sunday

    # Check if the selected date is a holiday
    holiday = None
    try:
        holiday = Holiday.objects.filter(date=attendance_date).first()
    except Exception:
        pass

    if selected_class_id:
        # Get the selected class name for display
        try:
            selected_class = StudentClass.objects.get(id=selected_class_id)
            selected_class_name = selected_class.name

            # Get all sections for this class
            sections = Student.objects.filter(
                current_class_id=selected_class_id,
                current_status='active'
            ).values_list('section', flat=True).distinct()

            # Filter students by class and section if provided
            student_query = Student.objects.filter(current_class_id=selected_class_id)
            if selected_section:
                student_query = student_query.filter(section=selected_section)

            students = student_query.filter(current_status='active')

            # Get existing attendance records for these students on the selected date
            attendance_records = Attendance.objects.filter(
                student__in=students,
                date=attendance_date
            ).select_related('student')

            # Create a dictionary of student_id -> attendance record
            attendance_dict = {record.student.id: record for record in attendance_records}

            # Attach attendance status and comment to each student
            for student in students:
                if student.id in attendance_dict:
                    record = attendance_dict[student.id]
                    student.attendance_status = record.status
                    student.attendance_comment = record.comment
                    student.is_holiday = record.is_holiday
                    student.holiday_name = record.holiday_name
                else:
                    # Set default status based on whether it's a Sunday or holiday
                    if is_sunday:
                        student.attendance_status = 'Sunday'
                        student.attendance_comment = 'Weekend'
                        student.is_holiday = True
                        student.holiday_name = 'Sunday'
                    elif holiday:
                        student.attendance_status = 'Holiday'
                        student.attendance_comment = holiday.name
                        student.is_holiday = True
                        student.holiday_name = holiday.name
                    else:
                        student.attendance_status = 'Absent'  # Default status
                        student.attendance_comment = ''
                        student.is_holiday = False
                        student.holiday_name = ''

            # Generate weekly attendance summary (past 7 days including today)
            for i in range(7):
                day_date = today - datetime.timedelta(days=i)
                if day_date >= one_week_ago:
                    # Check if this day is a Sunday
                    day_is_sunday = day_date.weekday() == 6

                    # Check if this day is a holiday
                    day_holiday = Holiday.objects.filter(date=day_date).first()

                    # Query for this day's attendance
                    day_query = Attendance.objects.filter(
                        student__current_class_id=selected_class_id,
                        date=day_date
                    )

                    if selected_section:
                        day_query = day_query.filter(student__section=selected_section)

                    present_count = day_query.filter(status="Present").count()
                    leave_count = day_query.filter(status="Leave").count()
                    absent_count = day_query.filter(status="Absent").count()
                    holiday_count = day_query.filter(status__in=["Holiday", "Sunday"]).count()

                    # Calculate total (if no records, use student count)
                    total_records = present_count + leave_count + absent_count + holiday_count
                    total_students = students.count()

                    # If no records exist but it's a Sunday or holiday, create a placeholder
                    if total_records == 0 and (day_is_sunday or day_holiday):
                        holiday_name = "Sunday" if day_is_sunday else day_holiday.name
                        status = "Sunday" if day_is_sunday else "Holiday"
                    else:
                        holiday_name = ""
                        status = ""

                    weekly_attendance.append({
                        'date': day_date,
                        'present': present_count,
                        'leave': leave_count,
                        'absent': absent_count,
                        'holiday': holiday_count,
                        'total': total_students,
                        'is_sunday': day_is_sunday,
                        'is_holiday': True if day_holiday else False,
                        'holiday_name': day_holiday.name if day_holiday else ("Sunday" if day_is_sunday else ""),
                        'status': status
                    })
        except StudentClass.DoesNotExist:
            pass

    # Get attendance statistics for the selected date, class, and section
    attendance_query = Attendance.objects.filter(date=attendance_date)

    if selected_class_id:
        attendance_query = attendance_query.filter(student__current_class_id=selected_class_id)

        if selected_section:
            attendance_query = attendance_query.filter(student__section=selected_section)

    present_leave = attendance_query.filter(status__in=["Present", "Leave"]).count()
    absent = attendance_query.filter(status="Absent").count()
    holiday_count = attendance_query.filter(status__in=["Holiday", "Sunday"]).count()

    # Get class teacher (placeholder - you can implement this based on your data model)
    class_teacher = None
    if selected_class_id:
        # This is a placeholder - replace with your actual logic to get class teacher
        class_teacher = "Class Teacher"  # Replace with actual teacher name if available

    context = {
        "classes": classes,
        "sections": sections,
        "students": students,
        "selected_class_id": selected_class_id,
        "selected_class_name": selected_class_name,
        "selected_section": selected_section,
        "attendance_date": attendance_date,
        "present_leave": present_leave,
        "absent": absent,
        "holiday_count": holiday_count,
        "class_teacher": class_teacher,
        "weekly_attendance": weekly_attendance,
        "today": today,
        "one_week_ago": one_week_ago,
        "is_sunday": is_sunday,
        "holiday": holiday,
    }

    try:
        context['staff'] = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        context['staff'] = None

    return render(request, 'TeacherDashboard/attendance/attendance_management.html', context)


@login_required
def teacher_get_students_for_attendance(request, class_id):
    """Get students for attendance marking - Teacher version"""
    selected_class = get_object_or_404(StudentClass, id=class_id)
    students = Student.objects.filter(current_class=selected_class)

    students_data = [
        {
            "id": student.id,
            "fullname": student.fullname,
            "registration_number": student.registration_number,
            "section": student.section,
        }
        for student in students
    ]
    return JsonResponse(students_data, safe=False)


@login_required
def teacher_submit_attendance(request):
    """Submit attendance for teachers"""
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        # Get attendance date from the form
        attendance_date_str = request.POST.get('attendance_date')
        today = timezone.now().date()
        one_week_ago = today - datetime.timedelta(days=7)

        if attendance_date_str:
            try:
                attendance_date = datetime.datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
                # Validate date range
                if attendance_date > today:
                    return JsonResponse({"message": "Cannot take attendance for future dates"}, status=400)
                if attendance_date < one_week_ago:
                    return JsonResponse({"message": "Cannot update attendance older than one week"}, status=400)
            except ValueError:
                return JsonResponse({"message": "Invalid date format"}, status=400)
        else:
            attendance_date = today

        # Check if the selected date is a Sunday
        is_sunday = attendance_date.weekday() == 6  # 6 represents Sunday

        # Check if the selected date is a holiday
        holiday = Holiday.objects.filter(date=attendance_date).first()

        # Process each student's attendance
        attendance_count = 0
        with transaction.atomic():
            for key, value in request.POST.items():
                if key.startswith("attendance_") and key != "attendance_date":
                    student_id = key.split("_")[1]
                    student = get_object_or_404(Student, id=student_id)
                    status = value
                    comment = request.POST.get(f"comment_{student_id}", "")

                    # Set holiday flags if it's a Sunday or holiday
                    is_holiday = False
                    holiday_name = ""

                    if status == "Sunday":
                        is_holiday = True
                        holiday_name = "Sunday"
                        comment = comment or "Weekend"
                    elif status == "Holiday":
                        is_holiday = True
                        holiday_name = holiday.name if holiday else "Holiday"
                        comment = comment or holiday_name

                    # Update or create attendance record
                    Attendance.objects.update_or_create(
                        student=student,
                        date=attendance_date,
                        defaults={
                            'status': status,
                            'comment': comment,
                            'is_holiday': is_holiday,
                            'holiday_name': holiday_name
                        }
                    )
                    attendance_count += 1

        # Return appropriate message based on date and type
        if is_sunday:
            message = f"Sunday attendance marked for {attendance_count} students!"
        elif holiday:
            message = f"Holiday ({holiday.name}) attendance marked for {attendance_count} students!"
        elif attendance_date == today:
            message = f"Today's attendance saved successfully for {attendance_count} students!"
        else:
            formatted_date = attendance_date.strftime('%d %b, %Y')
            message = f"Attendance for {formatted_date} updated successfully for {attendance_count} students!"

        return JsonResponse({
            "message": message,
            "count": attendance_count,
            "date": attendance_date.strftime('%Y-%m-%d'),
            "is_sunday": is_sunday,
            "is_holiday": True if holiday else False,
            "holiday_name": holiday.name if holiday else ""
        })

    except IntegrityError as e:
        return JsonResponse({"message": f"Database error: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"}, status=500)














@login_required
def teacher_attendance_reports(request):
    """Attendance reports for teachers"""
    classes = StudentClass.objects.all()
    selected_class_id = request.GET.get('class_id')
    selected_section = request.GET.get('section', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Default date range (last 30 days)
    today = timezone.now().date()
    if not date_from:
        date_from = today - datetime.timedelta(days=30)
    else:
        date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()

    if not date_to:
        date_to = today
    else:
        date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()

    attendance_data = []
    sections = []

    if selected_class_id:
        # Get sections for the selected class
        sections = Student.objects.filter(
            current_class_id=selected_class_id,
            current_status='active'
        ).values_list('section', flat=True).distinct()

        # Build query for attendance data
        attendance_query = Attendance.objects.filter(
            student__current_class_id=selected_class_id,
            date__range=[date_from, date_to]
        )

        if selected_section:
            attendance_query = attendance_query.filter(student__section=selected_section)

        # Get attendance statistics
        from django.db.models import Count, Q

        attendance_stats = attendance_query.aggregate(
            total_present=Count('id', filter=Q(status='Present')),
            total_absent=Count('id', filter=Q(status='Absent')),
            total_leave=Count('id', filter=Q(status='Leave')),
            total_holiday=Count('id', filter=Q(status__in=['Holiday', 'Sunday']))
        )

        # Get daily attendance summary
        daily_attendance = {}
        for record in attendance_query.values('date', 'status').annotate(count=Count('id')):
            date = record['date']
            status = record['status']
            if date not in daily_attendance:
                daily_attendance[date] = {'Present': 0, 'Absent': 0, 'Leave': 0, 'Holiday': 0, 'Sunday': 0}
            daily_attendance[date][status] = record['count']

        attendance_data = {
            'stats': attendance_stats,
            'daily': daily_attendance
        }

    context = {
        'classes': classes,
        'sections': sections,
        'selected_class_id': selected_class_id,
        'selected_section': selected_section,
        'date_from': date_from,
        'date_to': date_to,
        'attendance_data': attendance_data,
    }

    try:
        context['staff'] = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        context['staff'] = None

    return render(request, 'TeacherDashboard/attendance/attendance_reports.html', context)
