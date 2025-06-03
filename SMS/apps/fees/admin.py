from django.contrib import admin
from .models import FeePayment, PendingFee

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'payment_method', 'transaction_id', 'date', 'status', 'fee_category')
    list_filter = ('payment_method', 'status', 'date', 'fee_category')
    search_fields = ('student__fullname', 'transaction_id')
    date_hierarchy = 'date'

@admin.register(PendingFee)
class PendingFeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_type', 'amount', 'due_date', 'paid')
    list_filter = ('paid', 'due_date', 'fee_type')
    search_fields = ('student__fullname', 'fee_type')
    date_hierarchy = 'due_date'
