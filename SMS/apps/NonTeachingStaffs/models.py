from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class NonTeachingStaff(models.Model):
    STATUS = [("active", "Active"), ("inactive", "Inactive")]

    GENDER = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    fullname = models.CharField(max_length=200)

    
    gender = models.CharField(max_length=10, choices=GENDER, default="male")
    
    job_role = models.CharField(max_length=100, default='N/A')  

    date_of_birth = models.DateField(default=timezone.now)
    date_of_registration= models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )

    address = models.TextField(blank=True)
    others = models.TextField(blank=True)

    def __str__(self):
        return f"{self.fullname} "

    def get_absolute_url(self):
        return reverse("non-teaching-staffs-detail", kwargs={"pk": self.pk})
