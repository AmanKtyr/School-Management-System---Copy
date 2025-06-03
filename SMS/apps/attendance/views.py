# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.students.models import Student
from .models import Attendance, Holiday
from apps.corecode.models import StudentClass
import datetime

def attendance_list(request):
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
    return render(request, 'attendance/attendance_list.html', context)

def get_students(request, class_id):
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

def submit_attendance(request):
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
def holiday_list(request):
    """
    View for listing and managing holidays
    """
    today = timezone.now().date()

    # Get all holidays
    holidays = Holiday.objects.all().order_by('date')

    # Get upcoming holidays (from today onwards)
    upcoming_holidays = holidays.filter(date__gte=today)

    # Get past holidays (before today) for the current year
    year_start = datetime.date(today.year, 1, 1)
    past_holidays = holidays.filter(date__lt=today, date__gte=year_start)

    context = {
        "holidays": holidays,
        "upcoming_holidays": upcoming_holidays,
        "past_holidays": past_holidays,
        "today": today,
    }

    return render(request, 'attendance/holiday_list.html', context)


@login_required
def add_holiday(request):
    """
    View for adding a new holiday
    """
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        # Get form data
        date_str = request.POST.get('date')
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        # Validate required fields
        if not date_str or not name:
            messages.error(request, "Date and name are required")
            return redirect('attendance:holiday_list')

        # Parse date
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format")
            return redirect('attendance:holiday_list')

        # Check if a holiday already exists on this date
        if Holiday.objects.filter(date=date).exists():
            messages.warning(request, f"A holiday already exists on {date}")
            return redirect('attendance:holiday_list')

        # Create the holiday
        holiday = Holiday.objects.create(
            date=date,
            name=name,
            description=description
        )

        # Add success message
        messages.success(request, f"Holiday '{name}' added successfully!")
        return redirect('attendance:holiday_list')

    except IntegrityError as e:
        messages.error(request, f"Database error: {str(e)}")
        return redirect('attendance:holiday_list')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('attendance:holiday_list')


@login_required
def edit_holiday(request):
    """
    View for editing an existing holiday
    """
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        # Get form data
        holiday_id = request.POST.get('holiday_id')
        date_str = request.POST.get('date')
        name = request.POST.get('name')
        description = request.POST.get('description', '')

        # Validate required fields
        if not holiday_id or not date_str or not name:
            messages.error(request, "Holiday ID, date, and name are required")
            return redirect('attendance:holiday_list')

        # Get the holiday
        try:
            holiday = Holiday.objects.get(id=holiday_id)
        except Holiday.DoesNotExist:
            messages.error(request, "Holiday not found")
            return redirect('attendance:holiday_list')

        # Parse date
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format")
            return redirect('attendance:holiday_list')

        # Check if another holiday exists on this date (excluding this one)
        if Holiday.objects.filter(date=date).exclude(id=holiday_id).exists():
            messages.warning(request, f"Another holiday already exists on {date}")
            return redirect('attendance:holiday_list')

        # Update the holiday
        holiday.date = date
        holiday.name = name
        holiday.description = description
        holiday.save()

        # Update any attendance records that were marked with this holiday
        Attendance.objects.filter(
            date=holiday.date,
            status='Holiday',
            is_holiday=True
        ).update(holiday_name=name)

        # Add success message
        messages.success(request, f"Holiday '{name}' updated successfully!")
        return redirect('attendance:holiday_list')

    except IntegrityError as e:
        messages.error(request, f"Database error: {str(e)}")
        return redirect('attendance:holiday_list')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('attendance:holiday_list')


@login_required
def delete_holiday(request):
    """
    View for deleting a holiday
    """
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        # Get holiday ID
        holiday_id = request.POST.get('holiday_id')

        # Validate required fields
        if not holiday_id:
            messages.error(request, "Holiday ID is required")
            return redirect('attendance:holiday_list')

        # Get the holiday
        try:
            holiday = Holiday.objects.get(id=holiday_id)
        except Holiday.DoesNotExist:
            messages.error(request, "Holiday not found")
            return redirect('attendance:holiday_list')

        # Store holiday info for response
        holiday_name = holiday.name
        holiday_date = holiday.date

        # Delete the holiday
        holiday.delete()

        # Add success message
        messages.success(request, f"Holiday '{holiday_name}' on {holiday_date} deleted successfully!")
        return redirect('attendance:holiday_list')

    except IntegrityError as e:
        messages.error(request, f"Database error: {str(e)}")
        return redirect('attendance:holiday_list')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('attendance:holiday_list')
