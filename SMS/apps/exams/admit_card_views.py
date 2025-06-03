from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Exam, ExamSchedule, AdmitCard
from apps.students.models import Student

@login_required
def admit_card_bulk_action(request):
    """View for bulk actions on admit cards"""
    if request.method == 'POST':
        exam_id = request.POST.get('bulk_exam')
        class_id = request.POST.get('bulk_class')
        action = request.POST.get('bulk_action')

        if not exam_id or not action:
            messages.error(request, 'Please select an exam and action.')
            return redirect('exams:admit_card_list')

        # Get admit cards based on filters
        cards_query = AdmitCard.objects.filter(exam_id=exam_id)

        if class_id:
            cards_query = cards_query.filter(student__current_class_id=class_id)

        if action == 'generate':
            # Redirect to generate page with pre-filled filters
            return redirect(f'exams:admit_card_generate?exam={exam_id}&class={class_id or ""}')

        elif action == 'print':
            # Get IDs and redirect to print page
            card_ids = cards_query.values_list('id', flat=True)
            return redirect(f'exams:admit_card_print_bulk?ids={",".join(map(str, card_ids))}')

        elif action == 'delete':
            # Delete admit cards
            count = cards_query.count()
            cards_query.delete()
            messages.success(request, f'{count} admit card(s) deleted successfully.')

        return redirect('exams:admit_card_list')

    return redirect('exams:admit_card_list')

@login_required
def admit_card_view(request, pk):
    """View for viewing a single admit card"""
    admit_card = get_object_or_404(AdmitCard, pk=pk)

    # Get exam schedules for this exam
    exam_schedules = ExamSchedule.objects.filter(
        exam=admit_card.exam,
        student_class=admit_card.student.current_class
    ).order_by('date', 'start_time')

    if admit_card.student.section:
        exam_schedules = exam_schedules.filter(
            Q(section='') | Q(section=admit_card.student.section)
        )

    context = {
        'admit_cards': [admit_card],  # List for template reuse
        'exam_schedules': exam_schedules,
    }

    return render(request, 'exams/admit_card_print.html', context)

@login_required
def admit_card_print(request, pk):
    """View for printing a single admit card"""
    admit_card = get_object_or_404(AdmitCard, pk=pk)

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

    context = {
        'admit_cards': [admit_card],  # List for template reuse
        'exam_schedules': exam_schedules,
    }

    return render(request, 'exams/admit_card_print.html', context)

@login_required
def admit_card_print_bulk(request):
    """View for printing multiple admit cards"""
    ids = request.GET.get('ids', '')

    if not ids:
        messages.error(request, 'No admit cards selected for printing.')
        return redirect('exams:admit_card_list')

    id_list = ids.split(',')
    admit_cards = AdmitCard.objects.filter(pk__in=id_list)

    if not admit_cards.exists():
        messages.error(request, 'No valid admit cards found.')
        return redirect('exams:admit_card_list')

    # Mark all as printed
    now = timezone.now()
    for card in admit_cards:
        if not card.is_printed:
            card.is_printed = True
            card.printed_on = now
            card.save()

    # Get all unique exam IDs
    exam_ids = admit_cards.values_list('exam_id', flat=True).distinct()

    # Get all exam schedules for these exams
    exam_schedules = ExamSchedule.objects.filter(exam_id__in=exam_ids).order_by('date', 'start_time')

    context = {
        'admit_cards': admit_cards,
        'exam_schedules': exam_schedules,
    }

    return render(request, 'exams/admit_card_print.html', context)
