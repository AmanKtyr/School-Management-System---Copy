from django.contrib import admin
from .models import Holiday, Attendance

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'description')
    search_fields = ('name', 'date')
    list_filter = ('date',)
    date_hierarchy = 'date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'status', 'date', 'is_holiday', 'holiday_name')
    list_filter = ('status', 'date', 'is_holiday')
    search_fields = ('student__fullname', 'comment', 'holiday_name')
    date_hierarchy = 'date'
