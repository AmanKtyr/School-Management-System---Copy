from django.urls import path
from .views import (
    attendance_list, get_students, submit_attendance,
    holiday_list, add_holiday, edit_holiday, delete_holiday
)

urlpatterns = [
    path('attendance_list/', attendance_list, name='attendance_list'),
    path('get_students/<int:class_id>/', get_students, name='get_students'),
    path('submit_attendance/', submit_attendance, name='submit_attendance'),

    # Holiday management URLs
    path('holidays/', holiday_list, name='holiday_list'),
    path('holidays/add/', add_holiday, name='add_holiday'),
    path('holidays/edit/', edit_holiday, name='edit_holiday'),
    path('holidays/delete/', delete_holiday, name='delete_holiday'),
]
