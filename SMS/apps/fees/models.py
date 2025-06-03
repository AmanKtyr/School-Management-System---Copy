from django.db import models
from django.utils import timezone
from apps.corecode.models import FeeStructure

class PendingFee(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='pending_fees')
    fee_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.fullname} - {self.fee_type} - ₹{self.amount}"

    def get_discounted_amount(self):
        return self.amount - (self.amount * self.discount / 100)

class FeePayment(models.Model):
    PAYMENT_STATUS = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
    ]

    PAYMENT_METHODS = [
        ("Cash", "Cash"),
        ("Online", "Online"),
        ("Bank Transfer", "Bank Transfer")
    ]

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="Required for online or bank transfers")
    date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Pending")
    fee_category = models.CharField(max_length=50, default="Regular")

    def __str__(self):
        return f"{self.student.fullname} - ₹{self.amount}"
