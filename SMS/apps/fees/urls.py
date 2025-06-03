from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('', views.fee_list, name='fee_list'),
    path('add-payment/<int:student_id>/', views.add_fee_payment, name='add_fee_payment'),
    path('history/<int:student_id>/', views.student_fee_history, name='student_fee_history'),
    path('receipt/<int:payment_id>/', views.generate_receipt, name='generate_receipt'),
    path('complete-history/<int:student_id>/', views.generate_complete_history, name='generate_complete_history'),
    path('transactions/', views.all_transactions, name='all_transactions'),
]
