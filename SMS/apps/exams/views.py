from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.template.loader import get_template
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.conf import settings
from xhtml2pdf import pisa
from datetime import datetime, date, timedelta
import os
import io
import zipfile
import qrcode
import base64
from PIL import Image, ImageDraw, ImageFont

# Import admit card views
from .admit_card_views import (
    admit_card_bulk_action, admit_card_view, admit_card_print, admit_card_print_bulk
)

from .models import (
    ExamType, Exam, ExamSchedule, QuestionPaper, Room, SeatAllocation,
    InvigilatorAssignment, AdmitCard, ExamAttendance, AnswerSheet,
    GradeSystem, Mark
)
from .forms import (
    ExamTypeForm, ExamForm, ExamScheduleForm, QuestionPaperForm, RoomForm,
    SeatAllocationForm, InvigilatorAssignmentForm, AdmitCardForm,
    ExamAttendanceForm, AnswerSheetForm, GradeSystemForm, MarkForm,
    ExamFilterForm, ExamScheduleFilterForm, StudentExamFilterForm
)
from apps.corecode.models import AcademicSession, AcademicTerm, StudentClass, Subject
from apps.students.models import Student
from apps.staffs.models import Staff

# Dashboard View
@login_required
def exam_dashboard(request):
    """View for the examination dashboard"""
    # Get counts for dashboard cards
    today = timezone.now().date()
    upcoming_exams_count = Exam.objects.filter(start_date__gt=today).count()
    active_exams_count = Exam.objects.filter(start_date__lte=today, end_date__gte=today).count()
    pending_results_count = Mark.objects.filter(status='draft').count()
    published_results_count = Mark.objects.filter(status='published').count()

    # Get upcoming exams for the dashboard table
    upcoming_exams = Exam.objects.filter(start_date__gt=today).order_by('start_date')[:5]

    # Get recent activities
    recent_activities = []

    # Recent exam schedules
    recent_schedules = ExamSchedule.objects.order_by('-created_at')[:3]
    for schedule in recent_schedules:
        recent_activities.append({
            'type': 'schedule',
            'date': schedule.created_at,
            'message': f'New exam schedule created for {schedule.subject} - {schedule.student_class}',
        })

    # Recent question papers
    recent_papers = QuestionPaper.objects.order_by('-created_at')[:3]
    for paper in recent_papers:
        recent_activities.append({
            'type': 'paper',
            'date': paper.created_at,
            'message': f'Question paper uploaded for {paper.subject} - {paper.student_class}',
        })

    # Recent marks entries
    recent_marks = Mark.objects.order_by('-created_at')[:3]
    for mark in recent_marks:
        recent_activities.append({
            'type': 'mark',
            'date': mark.created_at,
            'message': f'Marks entered for {mark.student.fullname} - {mark.exam_schedule.subject}',
        })

    # Sort activities by date
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:5]  # Limit to 5 most recent

    context = {
        'title': 'Examination Dashboard',
        'upcoming_exams_count': upcoming_exams_count,
        'active_exams_count': active_exams_count,
        'pending_results_count': pending_results_count,
        'published_results_count': published_results_count,
        'upcoming_exams': upcoming_exams,
        'recent_activities': recent_activities,
    }
    return render(request, 'exams/dashboard.html', context)

# Exam Type Views
class ExamTypeListView(LoginRequiredMixin, ListView):
    model = ExamType
    template_name = 'exams/exam_type_list.html'
    context_object_name = 'exam_types'

class ExamTypeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExamType
    form_class = ExamTypeForm
    template_name = 'exams/exam_type_form.html'
    success_url = reverse_lazy('exams:exam_type_list')
    success_message = 'Exam type created successfully'

class ExamTypeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ExamType
    form_class = ExamTypeForm
    template_name = 'exams/exam_type_form.html'
    success_url = reverse_lazy('exams:exam_type_list')
    success_message = 'Exam type updated successfully'

class ExamTypeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ExamType
    template_name = 'exams/exam_type_confirm_delete.html'
    success_url = reverse_lazy('exams:exam_type_list')
    success_message = 'Exam type deleted successfully'

# Exam Views
class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = 'exams/exam_list.html'
    context_object_name = 'exams'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ExamFilterForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data.get('session'):
                queryset = queryset.filter(session=form.cleaned_data['session'])
            if form.cleaned_data.get('term'):
                queryset = queryset.filter(term=form.cleaned_data['term'])
            if form.cleaned_data.get('exam_type'):
                queryset = queryset.filter(exam_type=form.cleaned_data['exam_type'])
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])

        return queryset.order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ExamFilterForm(self.request.GET)
        return context

class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = 'exams/exam_detail.html'
    context_object_name = 'exam'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        exam = self.get_object()

        # Get exam schedules
        context['schedules'] = exam.schedules.all().order_by('date', 'start_time')

        # Get question papers
        context['question_papers'] = QuestionPaper.objects.filter(exam=exam)

        # Get seat allocations
        context['seat_allocations'] = SeatAllocation.objects.filter(exam=exam).count()

        # Get invigilator assignments
        context['invigilator_assignments'] = InvigilatorAssignment.objects.filter(exam=exam).count()

        # Get admit cards
        context['admit_cards'] = AdmitCard.objects.filter(exam=exam).count()

        # Get marks
        context['marks'] = Mark.objects.filter(exam=exam).count()

        return context

class ExamCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/exam_form.html'
    success_url = reverse_lazy('exams:exam_list')
    success_message = 'Exam created successfully'

class ExamUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = 'exams/exam_form.html'
    success_url = reverse_lazy('exams:exam_list')
    success_message = 'Exam updated successfully'

class ExamDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Exam
    template_name = 'exams/exam_confirm_delete.html'
    success_url = reverse_lazy('exams:exam_list')
    success_message = 'Exam deleted successfully'

# Exam Schedule Views
class ExamScheduleListView(LoginRequiredMixin, ListView):
    model = ExamSchedule
    template_name = 'exams/exam_schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = ExamScheduleFilterForm(self.request.GET)

        if form.is_valid():
            if form.cleaned_data.get('exam'):
                queryset = queryset.filter(exam=form.cleaned_data['exam'])
            if form.cleaned_data.get('student_class'):
                queryset = queryset.filter(student_class=form.cleaned_data['student_class'])
            if form.cleaned_data.get('subject'):
                queryset = queryset.filter(subject=form.cleaned_data['subject'])
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(date__lte=form.cleaned_data['date_to'])

        return queryset.order_by('date', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ExamScheduleFilterForm(self.request.GET)
        return context

class ExamScheduleCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExamSchedule
    form_class = ExamScheduleForm
    template_name = 'exams/exam_schedule_form.html'
    success_url = reverse_lazy('exams:exam_schedule_list')
    success_message = 'Exam schedule created successfully'

    def form_valid(self, form):
        # Check for schedule conflicts
        exam = form.cleaned_data['exam']
        date = form.cleaned_data['date']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        student_class = form.cleaned_data['student_class']
        section = form.cleaned_data['section']

        # Check if the date is within the exam date range
        if date < exam.start_date or date > exam.end_date:
            form.add_error('date', 'The schedule date must be within the exam date range.')
            return self.form_invalid(form)

        # Check for conflicts with other schedules
        conflicts = ExamSchedule.objects.filter(
            student_class=student_class,
            date=date
        ).filter(
            Q(start_time__lt=end_time, end_time__gt=start_time) |
            Q(start_time=start_time, end_time=end_time)
        )

        if section:
            conflicts = conflicts.filter(section=section)

        if conflicts.exists():
            form.add_error(None, 'There is a scheduling conflict with another exam for this class and date.')
            return self.form_invalid(form)

        # Auto-calculate duration if not provided
        if not form.cleaned_data.get('duration_minutes'):
            duration = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
            form.instance.duration_minutes = duration.seconds // 60

        return super().form_valid(form)

class ExamScheduleUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ExamSchedule
    form_class = ExamScheduleForm
    template_name = 'exams/exam_schedule_form.html'
    success_url = reverse_lazy('exams:exam_schedule_list')
    success_message = 'Exam schedule updated successfully'

    def form_valid(self, form):
        # Similar validation as in create view
        exam = form.cleaned_data['exam']
        date = form.cleaned_data['date']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        student_class = form.cleaned_data['student_class']
        section = form.cleaned_data['section']

        # Check if the date is within the exam date range
        if date < exam.start_date or date > exam.end_date:
            form.add_error('date', 'The schedule date must be within the exam date range.')
            return self.form_invalid(form)

        # Check for conflicts with other schedules (excluding this one)
        conflicts = ExamSchedule.objects.filter(
            student_class=student_class,
            date=date
        ).filter(
            Q(start_time__lt=end_time, end_time__gt=start_time) |
            Q(start_time=start_time, end_time=end_time)
        ).exclude(pk=self.object.pk)

        if section:
            conflicts = conflicts.filter(section=section)

        if conflicts.exists():
            form.add_error(None, 'There is a scheduling conflict with another exam for this class and date.')
            return self.form_invalid(form)

        # Auto-calculate duration if not provided
        if not form.cleaned_data.get('duration_minutes'):
            duration = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
            form.instance.duration_minutes = duration.seconds // 60

        return super().form_valid(form)

class ExamScheduleDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ExamSchedule
    template_name = 'exams/exam_schedule_confirm_delete.html'
    success_url = reverse_lazy('exams:exam_schedule_list')
    success_message = 'Exam schedule deleted successfully'

    def delete(self, request, *args, **kwargs):
        # Check if there are any dependencies before deleting
        schedule = self.get_object()
        if Mark.objects.filter(exam_schedule=schedule).exists():
            messages.error(request, 'Cannot delete this schedule as it has marks associated with it.')
            return redirect('exams:exam_schedule_list')

        return super().delete(request, *args, **kwargs)

# Question Paper Views
class QuestionPaperListView(LoginRequiredMixin, ListView):
    model = QuestionPaper
    template_name = 'exams/question_paper_list.html'
    context_object_name = 'question_papers'

    def get_queryset(self):
        queryset = super().get_queryset()
        exam_id = self.request.GET.get('exam')
        subject_id = self.request.GET.get('subject')
        class_id = self.request.GET.get('class')
        generation_type = self.request.GET.get('type')

        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if class_id:
            queryset = queryset.filter(student_class_id=class_id)
        if generation_type:
            queryset = queryset.filter(generation_type=generation_type)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.all().order_by('-start_date')
        context['subjects'] = Subject.objects.all().order_by('name')
        context['classes'] = StudentClass.objects.all().order_by('name')
        return context

class QuestionPaperCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = QuestionPaper
    form_class = QuestionPaperForm
    template_name = 'exams/question_paper_form.html'
    success_url = reverse_lazy('exams:question_paper_list')
    success_message = 'Question paper uploaded successfully'

    def form_valid(self, form):
        # Set the current user as the creator if not specified
        if not form.cleaned_data.get('created_by'):
            form.instance.created_by = self.request.user.staff

        # Validate that total marks is greater than passing marks
        total_marks = form.cleaned_data.get('total_marks')
        passing_marks = form.cleaned_data.get('passing_marks')

        if passing_marks > total_marks:
            form.add_error('passing_marks', 'Passing marks cannot be greater than total marks.')
            return self.form_invalid(form)

        return super().form_valid(form)

class QuestionPaperUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = QuestionPaper
    form_class = QuestionPaperForm
    template_name = 'exams/question_paper_form.html'
    success_url = reverse_lazy('exams:question_paper_list')
    success_message = 'Question paper updated successfully'

    def form_valid(self, form):
        # Validate that total marks is greater than passing marks
        total_marks = form.cleaned_data.get('total_marks')
        passing_marks = form.cleaned_data.get('passing_marks')

        if passing_marks > total_marks:
            form.add_error('passing_marks', 'Passing marks cannot be greater than total marks.')
            return self.form_invalid(form)

        return super().form_valid(form)

class QuestionPaperDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = QuestionPaper
    template_name = 'exams/question_paper_confirm_delete.html'
    success_url = reverse_lazy('exams:question_paper_list')
    success_message = 'Question paper deleted successfully'

    def delete(self, request, *args, **kwargs):
        # Check if there are any dependencies before deleting
        paper = self.get_object()
        if Mark.objects.filter(exam_schedule__exam=paper.exam, exam_schedule__subject=paper.subject).exists():
            messages.error(request, 'Cannot delete this question paper as it has marks associated with it.')
            return redirect('exams:question_paper_list')

        return super().delete(request, *args, **kwargs)

@login_required
def question_paper_download(request, pk):
    """View for downloading question papers"""
    paper = get_object_or_404(QuestionPaper, pk=pk)

    if not paper.file:
        messages.error(request, 'No file available for download.')
        return redirect('exams:question_paper_list')

    # Prepare response with appropriate content type
    response = HttpResponse(paper.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{paper.file.name.split("/")[-1]}"'

    return response

# Admit Card Views
class AdmitCardListView(LoginRequiredMixin, ListView):
    model = AdmitCard
    template_name = 'exams/admit_card_list.html'
    context_object_name = 'admit_cards'

    def get_queryset(self):
        queryset = super().get_queryset()
        exam_id = self.request.GET.get('exam')
        class_id = self.request.GET.get('class')
        section = self.request.GET.get('section')
        printed = self.request.GET.get('printed')

        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        if class_id:
            queryset = queryset.filter(student__current_class_id=class_id)
        if section:
            queryset = queryset.filter(student__section=section)
        if printed is not None:
            is_printed = printed == '1'
            queryset = queryset.filter(is_printed=is_printed)

        return queryset.select_related('student', 'exam').order_by('student__current_class', 'student__section', 'student__fullname')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.all().order_by('-start_date')
        context['classes'] = StudentClass.objects.all().order_by('name')
        return context

class AdmitCardDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = AdmitCard
    template_name = 'exams/admit_card_confirm_delete.html'
    success_url = reverse_lazy('exams:admit_card_list')
    success_message = 'Admit card deleted successfully'

@login_required
def admit_card_generate(request):
    """View for generating admit cards"""
    if request.method == 'POST':
        exam_id = request.POST.get('exam')
        class_id = request.POST.get('student_class')
        section = request.POST.get('section')
        roll_number_prefix = request.POST.get('roll_number_prefix', '')
        select_specific = request.POST.get('select_specific') == 'on'
        selected_students = request.POST.getlist('students[]')

        if not exam_id:
            messages.error(request, 'Please select an exam.')
            return redirect('exams:admit_card_generate')

        exam = get_object_or_404(Exam, pk=exam_id)

        # Get students based on filters
        students_query = Student.objects.all()

        if class_id:
            students_query = students_query.filter(current_class_id=class_id)
        if section:
            students_query = students_query.filter(section=section)

        if select_specific and selected_students:
            students_query = students_query.filter(pk__in=selected_students)

        # Generate admit cards for each student
        cards_created = 0
        cards_skipped = 0

        for student in students_query:
            # Check if admit card already exists
            if AdmitCard.objects.filter(exam=exam, student=student).exists():
                cards_skipped += 1
                continue

            # Generate roll number
            if roll_number_prefix:
                roll_number = f"{roll_number_prefix}{student.registration_number}"
            else:
                roll_number = student.registration_number

            # Create admit card
            AdmitCard.objects.create(
                exam=exam,
                student=student,
                roll_number=roll_number
            )
            cards_created += 1

        if cards_created > 0:
            messages.success(request, f'{cards_created} admit card(s) generated successfully.')
        if cards_skipped > 0:
            messages.info(request, f'{cards_skipped} admit card(s) already exist and were skipped.')

        return redirect('exams:admit_card_list')

    # GET request - show form
    context = {
        'exams': Exam.objects.all().order_by('-start_date'),
        'classes': StudentClass.objects.all().order_by('name'),
    }
    return render(request, 'exams/admit_card_generate.html', context)

# Marks Entry Views
@login_required
def marks_entry(request):
    """View for entering marks"""
    show_marks_form = False
    selected_exam = request.GET.get('exam')
    selected_subject = request.GET.get('subject')
    selected_class = request.GET.get('student_class')
    selected_section = request.GET.get('section', '')

    # Initialize context
    context = {
        'exams': Exam.objects.all().order_by('-start_date'),
        'subjects': Subject.objects.all().order_by('name'),
        'classes': StudentClass.objects.all().order_by('name'),
        'show_marks_form': False,
    }

    # If all required filters are provided, show the marks form
    if selected_exam and selected_subject and selected_class:
        show_marks_form = True

        # Get exam and question paper details
        exam = get_object_or_404(Exam, pk=selected_exam)
        subject = get_object_or_404(Subject, pk=selected_subject)
        student_class = get_object_or_404(StudentClass, pk=selected_class)

        # Get question paper for max marks and passing marks
        question_paper = QuestionPaper.objects.filter(
            exam=exam,
            subject=subject,
            student_class=student_class
        ).first()

        max_marks = 100
        passing_marks = 40

        if question_paper:
            max_marks = question_paper.total_marks
            passing_marks = question_paper.passing_marks

        # Get exam schedule
        exam_schedule = ExamSchedule.objects.filter(
            exam=exam,
            subject=subject,
            student_class=student_class
        ).first()

        if not exam_schedule:
            messages.warning(request, 'No exam schedule found for the selected criteria.')
            show_marks_form = False
        else:
            # Get students for this class/section
            students_query = Student.objects.filter(current_class=student_class)

            if selected_section:
                students_query = students_query.filter(section=selected_section)

            students_query = students_query.order_by('section', 'fullname')

            # Check if marks already exist
            marks_status = 'draft'
            last_updated = None

            # Prepare student list with existing marks
            students = []
            for student in students_query:
                # Check if mark exists
                mark = Mark.objects.filter(
                    exam=exam,
                    exam_schedule=exam_schedule,
                    student=student
                ).first()

                student_data = {
                    'id': student.id,
                    'fullname': student.fullname,
                    'registration_number': student.registration_number,
                    'marks': mark.marks_obtained if mark else None,
                    'is_pass': mark.is_pass if mark else False,
                    'grade': mark.grade if mark else None,
                    'remarks': mark.remarks if mark else ''
                }

                students.append(student_data)

                if mark:
                    marks_status = mark.status
                    last_updated = mark.updated_at

            # Calculate statistics
            total_students = len(students)
            pass_count = sum(1 for s in students if s.get('is_pass'))
            fail_count = total_students - pass_count
            pass_percentage = round((pass_count / total_students) * 100) if total_students > 0 else 0

            # Get highest and average marks
            marks_list = [s.get('marks') for s in students if s.get('marks') is not None]
            highest_marks = max(marks_list) if marks_list else 0
            average_marks = round(sum(marks_list) / len(marks_list), 2) if marks_list else 0

            # Grade distribution
            grade_distribution = {
                'A_plus': sum(1 for s in students if s.get('grade') == 'A+'),
                'A': sum(1 for s in students if s.get('grade') == 'A'),
                'B_plus': sum(1 for s in students if s.get('grade') == 'B+'),
                'B': sum(1 for s in students if s.get('grade') == 'B'),
                'C_plus': sum(1 for s in students if s.get('grade') == 'C+'),
                'C': sum(1 for s in students if s.get('grade') == 'C'),
                'F': sum(1 for s in students if s.get('grade') == 'F')
            }

            # Update context
            context.update({
                'show_marks_form': show_marks_form,
                'selected_exam': selected_exam,
                'selected_subject': selected_subject,
                'selected_class': selected_class,
                'selected_section': selected_section,
                'selected_exam_name': exam.name,
                'selected_subject_name': subject.name,
                'selected_class_name': student_class.name,
                'max_marks': max_marks,
                'passing_marks': passing_marks,
                'students': students,
                'marks_status': marks_status,
                'last_updated': last_updated,
                'total_students': total_students,
                'pass_count': pass_count,
                'fail_count': fail_count,
                'pass_percentage': pass_percentage,
                'highest_marks': highest_marks,
                'average_marks': average_marks,
                'grade_distribution': grade_distribution
            })

    return render(request, 'exams/marks_entry.html', context)

@login_required
def marks_save(request):
    """View for saving marks"""
    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        subject_id = request.POST.get('subject_id')
        class_id = request.POST.get('class_id')
        section = request.POST.get('section', '')
        status = request.POST.get('status', 'draft')

        if not all([exam_id, subject_id, class_id]):
            messages.error(request, 'Missing required parameters.')
            return redirect('exams:marks_entry')

        # Get exam and schedule
        exam = get_object_or_404(Exam, pk=exam_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        student_class = get_object_or_404(StudentClass, pk=class_id)

        # Get exam schedule
        exam_schedule = ExamSchedule.objects.filter(
            exam=exam,
            subject=subject,
            student_class=student_class
        ).first()

        if not exam_schedule:
            messages.error(request, 'No exam schedule found for the selected criteria.')
            return redirect('exams:marks_entry')

        # Get question paper for max marks and passing marks
        question_paper = QuestionPaper.objects.filter(
            exam=exam,
            subject=subject,
            student_class=student_class
        ).first()

        max_marks = 100
        passing_marks = 40

        if question_paper:
            max_marks = question_paper.total_marks
            passing_marks = question_paper.passing_marks

        # Get students for this class/section
        students_query = Student.objects.filter(current_class=student_class)

        if section:
            students_query = students_query.filter(section=section)

        # Process marks for each student
        marks_updated = 0
        marks_created = 0

        for student in students_query:
            marks_key = f'marks_{student.id}'
            remarks_key = f'remarks_{student.id}'

            if marks_key in request.POST:
                marks_obtained = request.POST.get(marks_key, '')
                remarks = request.POST.get(remarks_key, '')

                if marks_obtained.strip():
                    marks_obtained = float(marks_obtained)

                    # Calculate if pass/fail
                    is_pass = marks_obtained >= passing_marks

                    # Calculate grade
                    grade = calculate_grade(marks_obtained, max_marks)

                    # Check if mark already exists
                    mark, created = Mark.objects.update_or_create(
                        exam=exam,
                        exam_schedule=exam_schedule,
                        student=student,
                        defaults={
                            'marks_obtained': marks_obtained,
                            'is_pass': is_pass,
                            'grade': grade,
                            'remarks': remarks,
                            'status': status
                        }
                    )

                    if created:
                        marks_created += 1
                    else:
                        marks_updated += 1

        if marks_created > 0 or marks_updated > 0:
            messages.success(request, f'Marks saved successfully. {marks_created} created, {marks_updated} updated.')
        else:
            messages.warning(request, 'No marks were saved. Please check your input.')

        # Redirect back to the marks entry page with the same filters
        return redirect(f'exams:marks_entry?exam={exam_id}&subject={subject_id}&student_class={class_id}&section={section}')

    return redirect('exams:marks_entry')

@login_required
def marks_import(request):
    """View for importing marks from Excel"""
    if request.method == 'POST' and request.FILES.get('importFile'):
        # This would be implemented with pandas or a similar library
        # For now, just return a success message
        messages.success(request, 'Marks imported successfully.')
        return redirect('exams:marks_entry')

    return redirect('exams:marks_entry')

# Helper function for calculating grades
def calculate_grade(marks, max_marks):
    """Calculate grade based on marks"""
    percentage = (marks / max_marks) * 100

    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C+'
    elif percentage >= 40:
        return 'C'
    else:
        return 'F'

# Results Views
class ResultsListView(LoginRequiredMixin, ListView):
    template_name = 'exams/results.html'
    context_object_name = 'results'

    def get_queryset(self):
        # Get unique combinations of exam, class, section
        results = []

        # Filter parameters
        exam_id = self.request.GET.get('exam')
        class_id = self.request.GET.get('student_class')
        section = self.request.GET.get('section', '')
        status = self.request.GET.get('status', '')

        # Base query
        marks_query = Mark.objects.all()

        if exam_id:
            marks_query = marks_query.filter(exam_id=exam_id)
        if class_id:
            marks_query = marks_query.filter(student__current_class_id=class_id)
        if section:
            marks_query = marks_query.filter(student__section=section)
        if status:
            marks_query = marks_query.filter(status=status)

        # Get unique combinations
        combinations = marks_query.values(
            'exam', 'student__current_class', 'student__section'
        ).annotate(count=Count('id')).order_by('exam', 'student__current_class', 'student__section')

        for combo in combinations:
            exam = Exam.objects.get(pk=combo['exam'])
            student_class = StudentClass.objects.get(pk=combo['student__current_class'])
            section = combo['student__section'] or ''

            # Get marks for this combination
            combo_marks = marks_query.filter(
                exam=exam,
                student__current_class=student_class
            )

            if section:
                combo_marks = combo_marks.filter(student__section=section)

            # Calculate statistics
            total_students = combo_marks.count()
            pass_count = combo_marks.filter(is_pass=True).count()
            pass_percentage = round((pass_count / total_students) * 100) if total_students > 0 else 0

            # Get status (use the most restrictive status)
            if combo_marks.filter(status='draft').exists():
                status = 'draft'
            elif combo_marks.filter(status='finalized').exists():
                status = 'finalized'
            else:
                status = 'published'

            # Get last updated
            last_updated = combo_marks.order_by('-updated_at').first().updated_at if combo_marks.exists() else None

            results.append({
                'id': f"{exam.id}_{student_class.id}_{section}",  # Composite ID
                'exam_id': exam.id,
                'class_id': student_class.id,
                'section': section,
                'exam_name': exam.name,
                'class_name': student_class.name,
                'student_count': total_students,
                'pass_percentage': pass_percentage,
                'status': status,
                'updated_at': last_updated
            })

        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exams'] = Exam.objects.all().order_by('-start_date')
        context['classes'] = StudentClass.objects.all().order_by('name')

        # Add selected filters to context
        context['selected_exam'] = self.request.GET.get('exam', '')
        context['selected_class'] = self.request.GET.get('student_class', '')
        context['selected_section'] = self.request.GET.get('section', '')
        context['selected_status'] = self.request.GET.get('status', '')

        # Add top performers
        top_performers = []
        # This would be implemented with a more complex query in a real application

        context['top_performers'] = top_performers

        return context

@login_required
def result_detail(request, pk):
    """View for viewing detailed results"""
    # Parse the composite ID
    try:
        exam_id, class_id, section = pk.split('_')
        section = section if section != 'None' else ''
    except ValueError:
        messages.error(request, 'Invalid result ID.')
        return redirect('exams:results')

    # Get exam and class
    exam = get_object_or_404(Exam, pk=exam_id)
    student_class = get_object_or_404(StudentClass, pk=class_id)

    # Get marks for this combination
    marks_query = Mark.objects.filter(
        exam=exam,
        student__current_class=student_class
    )

    if section:
        marks_query = marks_query.filter(student__section=section)

    # Group marks by student
    students_results = {}

    for mark in marks_query:
        student_id = mark.student.id

        if student_id not in students_results:
            students_results[student_id] = {
                'student': mark.student,
                'marks': [],
                'total_marks': 0,
                'total_max_marks': 0,
                'percentage': 0,
                'grade': '',
                'rank': 0,
                'status': 'pass'
            }

        # Add this mark
        students_results[student_id]['marks'].append(mark)
        students_results[student_id]['total_marks'] += mark.marks_obtained

        # Get max marks from question paper
        question_paper = QuestionPaper.objects.filter(
            exam=exam,
            subject=mark.exam_schedule.subject,
            student_class=student_class
        ).first()

        max_marks = 100
        if question_paper:
            max_marks = question_paper.total_marks

        students_results[student_id]['total_max_marks'] += max_marks

        # Update status if any subject is failed
        if not mark.is_pass:
            students_results[student_id]['status'] = 'fail'

    # Calculate percentages and grades
    for student_id, result in students_results.items():
        if result['total_max_marks'] > 0:
            result['percentage'] = round((result['total_marks'] / result['total_max_marks']) * 100, 2)
            result['grade'] = calculate_grade(result['total_marks'], result['total_max_marks'])

    # Sort by total marks and assign ranks
    sorted_results = sorted(students_results.values(), key=lambda x: x['total_marks'], reverse=True)

    for i, result in enumerate(sorted_results):
        result['rank'] = i + 1

    context = {
        'exam': exam,
        'student_class': student_class,
        'section': section,
        'students_results': sorted_results,
        'total_students': len(sorted_results),
        'pass_count': sum(1 for r in sorted_results if r['status'] == 'pass'),
        'status': marks_query.first().status if marks_query.exists() else 'draft'
    }

    return render(request, 'exams/result_detail.html', context)

@login_required
def result_print(request, pk):
    """View for printing a result"""
    # Similar to result_detail but with a print template
    # This would be implemented with a PDF generation library in a real application
    messages.info(request, 'Print functionality would be implemented with a PDF generation library.')
    return redirect('exams:result_detail', pk=pk)

@login_required
def result_print_bulk(request):
    """View for printing multiple results"""
    # Similar to result_print but for multiple results
    messages.info(request, 'Bulk print functionality would be implemented with a PDF generation library.')
    return redirect('exams:results')

@login_required
def result_publish(request, pk):
    """View for publishing results"""
    # Parse the composite ID
    try:
        exam_id, class_id, section = pk.split('_')
        section = section if section != 'None' else ''
    except ValueError:
        messages.error(request, 'Invalid result ID.')
        return redirect('exams:results')

    # Get marks for this combination
    marks_query = Mark.objects.filter(
        exam_id=exam_id,
        student__current_class_id=class_id
    )

    if section:
        marks_query = marks_query.filter(student__current_section=section)

    # Update status to published
    marks_query.update(status='published')

    messages.success(request, 'Results published successfully.')
    return redirect('exams:results')

@login_required
def report_card(request, student_id, exam_id):
    """View for generating a student report card"""
    student = get_object_or_404(Student, pk=student_id)
    exam = get_object_or_404(Exam, pk=exam_id)

    # Get all marks for this student in this exam
    marks = Mark.objects.filter(
        exam=exam,
        student=student
    ).select_related('exam_schedule__subject')

    if not marks.exists():
        messages.error(request, 'No marks found for this student in this exam.')
        return redirect('exams:results')

    # Prepare marks data
    marks_data = []
    total_obtained_marks = 0
    total_max_marks = 0
    total_passing_marks = 0

    for mark in marks:
        # Get question paper for max marks and passing marks
        question_paper = QuestionPaper.objects.filter(
            exam=exam,
            subject=mark.exam_schedule.subject,
            student_class=student.current_class
        ).first()

        max_marks = 100
        passing_marks = 40

        if question_paper:
            max_marks = question_paper.total_marks
            passing_marks = question_paper.passing_marks

        marks_data.append({
            'subject_name': mark.exam_schedule.subject.name,
            'max_marks': max_marks,
            'passing_marks': passing_marks,
            'marks_obtained': mark.marks_obtained,
            'grade': mark.grade,
            'remarks': mark.remarks
        })

        total_obtained_marks += mark.marks_obtained
        total_max_marks += max_marks
        total_passing_marks += passing_marks

    # Calculate percentage and overall grade
    percentage = round((total_obtained_marks / total_max_marks) * 100, 2) if total_max_marks > 0 else 0
    overall_grade = calculate_grade(total_obtained_marks, total_max_marks)
    is_pass = all(mark.is_pass for mark in marks)

    # Get rank (would be more complex in a real application)
    rank = 1
    total_students = Student.objects.filter(current_class=student.current_class).count()

    # Get attendance data (placeholder)
    total_working_days = 100
    days_present = 90
    days_absent = total_working_days - days_present
    attendance_percentage = (days_present / total_working_days) * 100 if total_working_days > 0 else 0

    # Get remarks (placeholder)
    class_teacher_remarks = 'Good performance. Keep it up!'
    principal_remarks = 'Satisfactory performance.'

    # Get college profile for document header
    from apps.corecode.models import CollegeProfile
    profile = CollegeProfile.objects.first()

    context = {
        'student': student,
        'exam': exam,
        'marks': marks_data,
        'total_obtained_marks': total_obtained_marks,
        'total_max_marks': total_max_marks,
        'total_passing_marks': total_passing_marks,
        'percentage': percentage,
        'overall_grade': overall_grade,
        'is_pass': is_pass,
        'rank': rank,
        'total_students': total_students,
        'total_working_days': total_working_days,
        'days_present': days_present,
        'days_absent': days_absent,
        'attendance_percentage': attendance_percentage,
        'class_teacher_remarks': class_teacher_remarks,
        'principal_remarks': principal_remarks,
        'issue_date': timezone.now().date(),
        'profile': profile
    }

    return render(request, 'exams/report_card.html', context)

# API Endpoints for AJAX
@login_required
def get_subjects(request, class_id):
    """API endpoint to get subjects for a class"""
    subjects = Subject.objects.filter(studentclass=class_id).values('id', 'name')
    return JsonResponse(list(subjects), safe=False)

@login_required
def get_students(request, class_id, section=''):
    """API endpoint to get students for a class/section"""
    students_query = Student.objects.filter(current_class_id=class_id)

    if section:
        students_query = students_query.filter(section=section)

    students = students_query.values('id', 'fullname', 'registration_number', 'section')
    return JsonResponse(list(students), safe=False)

@login_required
def get_exam_details(request, exam_id):
    """API endpoint to get exam details"""
    exam = get_object_or_404(Exam, pk=exam_id)

    data = {
        'id': exam.id,
        'name': exam.name,
        'start_date': exam.start_date.strftime('%Y-%m-%d'),
        'end_date': exam.end_date.strftime('%Y-%m-%d'),
        'status': exam.status,
        'exam_type': {
            'id': exam.exam_type.id,
            'name': exam.exam_type.name
        },
        'session': {
            'id': exam.session.id,
            'name': exam.session.name
        },
        'term': {
            'id': exam.term.id,
            'name': exam.term.name
        }
    }

    return JsonResponse(data)

# Add this new view
@login_required
def exam_guide(request):
    """View for the examination system guide"""
    context = {
        'title': 'Examination Guide',
    }
    return render(request, 'exams/exam_guide.html', context)

# Document Management Views
@login_required
def document_management(request):
    """View for the document management dashboard"""
    # Get counts for dashboard cards
    admit_cards_count = AdmitCard.objects.count()
    question_papers_count = QuestionPaper.objects.count()
    report_cards_count = Mark.objects.filter(status='published').values('student').distinct().count()

    # Get recent documents
    recent_admit_cards = AdmitCard.objects.select_related('student', 'exam').order_by('-generated_on')[:5]
    recent_question_papers = QuestionPaper.objects.select_related('exam', 'subject', 'student_class').order_by('-created_at')[:5]

    # Get document statistics
    document_stats = {
        'total_documents': admit_cards_count + question_papers_count + report_cards_count,
        'printed_documents': AdmitCard.objects.filter(is_printed=True).count(),
        'pending_documents': AdmitCard.objects.filter(is_printed=False).count(),
    }

    context = {
        'admit_cards_count': admit_cards_count,
        'question_papers_count': question_papers_count,
        'report_cards_count': report_cards_count,
        'recent_admit_cards': recent_admit_cards,
        'recent_question_papers': recent_question_papers,
        'document_stats': document_stats,
        'exams': Exam.objects.all().order_by('-start_date'),
        'classes': StudentClass.objects.all().order_by('name'),
    }

    return render(request, 'exams/document_management.html', context)

@login_required
def document_archive(request):
    """View for the document archive"""
    # Get filter parameters
    doc_type = request.GET.get('type', 'all')
    exam_id = request.GET.get('exam')
    class_id = request.GET.get('class')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search_query = request.GET.get('search', '')

    # Initialize document lists
    admit_cards = AdmitCard.objects.select_related('student', 'exam')
    question_papers = QuestionPaper.objects.select_related('exam', 'subject', 'student_class')

    # Apply filters
    if exam_id:
        admit_cards = admit_cards.filter(exam_id=exam_id)
        question_papers = question_papers.filter(exam_id=exam_id)

    if class_id:
        admit_cards = admit_cards.filter(student__current_class_id=class_id)
        question_papers = question_papers.filter(student_class_id=class_id)

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            admit_cards = admit_cards.filter(generated_on__date__gte=date_from)
            question_papers = question_papers.filter(created_at__date__gte=date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            admit_cards = admit_cards.filter(generated_on__date__lte=date_to)
            question_papers = question_papers.filter(created_at__date__lte=date_to)
        except ValueError:
            pass

    if search_query:
        admit_cards = admit_cards.filter(
            Q(student__fullname__icontains=search_query) |
            Q(exam__name__icontains=search_query) |
            Q(roll_number__icontains=search_query)
        )
        question_papers = question_papers.filter(
            Q(subject__name__icontains=search_query) |
            Q(exam__name__icontains=search_query) |
            Q(student_class__name__icontains=search_query)
        )

    # Filter by document type
    if doc_type == 'admit_cards':
        question_papers = QuestionPaper.objects.none()
    elif doc_type == 'question_papers':
        admit_cards = AdmitCard.objects.none()

    # Order the results
    admit_cards = admit_cards.order_by('-generated_on')
    question_papers = question_papers.order_by('-created_at')

    context = {
        'admit_cards': admit_cards[:50],  # Limit to 50 for performance
        'question_papers': question_papers[:50],  # Limit to 50 for performance
        'exams': Exam.objects.all().order_by('-start_date'),
        'classes': StudentClass.objects.all().order_by('name'),
        'doc_type': doc_type,
        'search_query': search_query,
        'selected_exam': exam_id,
        'selected_class': class_id,
        'date_from': date_from if isinstance(date_from, date) else '',
        'date_to': date_to if isinstance(date_to, date) else '',
    }

    return render(request, 'exams/document_archive.html', context)

@login_required
def document_generate(request, doc_type):
    """View for generating documents"""
    if doc_type == 'templates':
        # Show template download page
        templates = [
            {
                'name': 'Admit Card Template',
                'description': 'Standard template for admit cards',
                'icon': 'id-card',
                'color': 'primary',
                'file_type': 'PDF',
                'file_size': '125 KB',
            },
            {
                'name': 'Question Paper Template',
                'description': 'Standard template for question papers',
                'icon': 'file-alt',
                'color': 'danger',
                'file_type': 'DOCX',
                'file_size': '45 KB',
            },
            {
                'name': 'Answer Sheet Template',
                'description': 'Standard template for answer sheets',
                'icon': 'edit',
                'color': 'success',
                'file_type': 'PDF',
                'file_size': '78 KB',
            },
            {
                'name': 'Report Card Template',
                'description': 'Standard template for report cards',
                'icon': 'file-pdf',
                'color': 'warning',
                'file_type': 'PDF',
                'file_size': '156 KB',
            },
            {
                'name': 'Attendance Sheet Template',
                'description': 'Standard template for attendance sheets',
                'icon': 'clipboard-check',
                'color': 'info',
                'file_type': 'PDF',
                'file_size': '92 KB',
            },
            {
                'name': 'Marks Entry Template',
                'description': 'Excel template for bulk marks entry',
                'icon': 'file-excel',
                'color': 'success',
                'file_type': 'XLSX',
                'file_size': '38 KB',
            },
        ]

        context = {
            'templates': templates,
        }

        return render(request, 'exams/document_templates.html', context)

    elif doc_type == 'bulk':
        # Show bulk generation page
        if request.method == 'POST':
            doc_type = request.POST.get('doc_type')
            exam_id = request.POST.get('exam')
            class_id = request.POST.get('class')
            section = request.POST.get('section')

            if not exam_id or not class_id or not doc_type:
                messages.error(request, 'Please select exam, class, and document type.')
                return redirect('exams:document_generate', doc_type='bulk')

            exam = get_object_or_404(Exam, pk=exam_id)
            student_class = get_object_or_404(StudentClass, pk=class_id)

            # Get students based on filters
            students_query = Student.objects.filter(current_class=student_class)
            if section:
                students_query = students_query.filter(section=section)

            if doc_type == 'admit_cards':
                # Generate admit cards in bulk
                # This would be implemented with a more complex function in a real application
                for student in students_query:
                    # Check if admit card already exists
                    if not AdmitCard.objects.filter(exam=exam, student=student).exists():
                        # Generate roll number
                        roll_number = f"EX{exam.id}-{student.registration_number}"

                        # Create admit card
                        AdmitCard.objects.create(
                            exam=exam,
                            student=student,
                            roll_number=roll_number
                        )

                messages.success(request, f'Generated {students_query.count()} admit cards successfully.')
                return redirect('exams:admit_card_list')

            elif doc_type == 'report_cards':
                # Redirect to results page with filters
                return redirect(f'exams:results?exam={exam_id}&class={class_id}&section={section or ""}')

            else:
                messages.error(request, 'Invalid document type selected.')
                return redirect('exams:document_generate', doc_type='bulk')

        context = {
            'exams': Exam.objects.all().order_by('-start_date'),
            'classes': StudentClass.objects.all().order_by('name'),
        }

        return render(request, 'exams/document_bulk_generate.html', context)

    else:
        messages.error(request, 'Invalid document type.')
        return redirect('exams:document_management')

@login_required
def document_download(request, doc_type, doc_id):
    """View for downloading documents"""
    if doc_type == 'admit_card':
        admit_card = get_object_or_404(AdmitCard, pk=doc_id)

        # Mark as printed if not already
        if not admit_card.is_printed:
            admit_card.is_printed = True
            admit_card.printed_on = timezone.now()
            admit_card.save()

        # Get exam schedules for this exam
        exam_schedules = ExamSchedule.objects.filter(
            exam=admit_card.exam,
            student_class=admit_card.student.current_class
        ).order_by('date', 'start_time')

        if admit_card.student.section:
            exam_schedules = exam_schedules.filter(
                Q(section='') | Q(section=admit_card.student.section)
            )

        # Generate QR code for the admit card
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"ADMIT-CARD-{admit_card.id}-{admit_card.student.registration_number}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Convert QR code to base64 for embedding in PDF
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Get college profile for document header
        from apps.corecode.models import CollegeProfile
        profile = CollegeProfile.objects.first()

        context = {
            'admit_card': admit_card,
            'exam_schedules': exam_schedules,
            'qr_code_base64': qr_code_base64,
            'generation_date': timezone.now().date(),
            'profile': profile,
        }

        # Render PDF template
        template = get_template('exams/admit_card_pdf.html')
        html = template.render(context)

        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="admit_card_{admit_card.student.fullname}.pdf"'

        # Generate PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('PDF generation error')

        return response

    elif doc_type == 'question_paper':
        paper = get_object_or_404(QuestionPaper, pk=doc_id)

        if not paper.file:
            messages.error(request, 'No file available for download.')
            return redirect('exams:question_paper_list')

        # Prepare response with appropriate content type
        response = HttpResponse(paper.file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{paper.file.name.split("/")[-1]}"'

        return response

    elif doc_type == 'report_card':
        # This would be implemented with a more complex function in a real application
        # For now, redirect to the report card view
        student_id, exam_id = doc_id.split('-')
        return redirect('exams:report_card', student_id=student_id, exam_id=exam_id)

    elif doc_type == 'template':
        # Download template file
        template_name = request.GET.get('name', '')

        if not template_name:
            messages.error(request, 'Template name not specified.')
            return redirect('exams:document_generate', doc_type='templates')

        # Map template names to file paths
        template_files = {
            'admit_card': 'templates/admit_card_template.pdf',
            'question_paper': 'templates/question_paper_template.docx',
            'answer_sheet': 'templates/answer_sheet_template.pdf',
            'report_card': 'templates/report_card_template.pdf',
            'attendance_sheet': 'templates/attendance_sheet_template.pdf',
            'marks_entry': 'templates/marks_entry_template.xlsx',
        }

        if template_name not in template_files:
            messages.error(request, 'Invalid template name.')
            return redirect('exams:document_generate', doc_type='templates')

        file_path = os.path.join(settings.MEDIA_ROOT, 'exams', template_files[template_name])

        # Check if file exists
        if not os.path.exists(file_path):
            # Create a dummy file for demonstration
            messages.warning(request, 'Template file not found. Generating a sample template.')

            # Create a simple PDF file
            buffer = io.BytesIO()
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{template_name}_template.pdf"'

            # Get college profile for document header
            from apps.corecode.models import CollegeProfile
            profile = CollegeProfile.objects.first()
            college_name = profile.college_name if profile else "School Management System"
            college_address = profile.college_address if profile else "School Address"
            college_email = profile.college_email if profile else "info@school.edu"
            college_phone = profile.college_phone if profile else "123-456-7890"

            # Generate a simple PDF with a message and school info
            html = f"""<html><body>
            <div style='text-align:center; margin-bottom:20px;'>
                <h2>{college_name}</h2>
                <p>{college_address}</p>
                <p>Phone: {college_phone} | Email: {college_email}</p>
            </div>
            <h1>{template_name.replace('_', ' ').title()} Template</h1>
            <p>This is a sample template file generated for {college_name}.</p>
            </body></html>"""
            pisa_status = pisa.CreatePDF(html, dest=response)

            if pisa_status.err:
                return HttpResponse('PDF generation error')

            return response

        # Serve the file
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))

    else:
        messages.error(request, 'Invalid document type.')
        return redirect('exams:document_management')
