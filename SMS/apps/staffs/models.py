from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
import random

class Staff(models.Model):
    STATUS = [("active", "Active"), ("inactive", "Inactive")]
    GENDER = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    registration_number = models.CharField(max_length=200, unique=True)
    fullname = models.CharField(max_length=200)
    gender = models.CharField(max_length=10, choices=GENDER, default="male")
    date_of_birth = models.DateField(default=timezone.now)
    date_of_registration = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField(validators=[mobile_num_regex], max_length=13, blank=True)
    aadhar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Aadhaar number must be exactly 12 digits.",
    code='invalid_aadhar'
    )
    aadhar = models.CharField(validators=[aadhar_validator], max_length=12, blank=True)
    Subject_specification = models.TextField(blank=True)
    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="staffs/passports/")



    def registration_number(self):
      if self.date_of_registration:
        year_suffix = str(self. date_of_registration.year)[-2:]  # Extract last 2 digits of year
      else:
        year_suffix = "25"  # Default if date_of_admission is missing

      unique_number = str(random.randint(1000, 9999))
      return f"{year_suffix}{unique_number}"

    def __str__(self):
        return f"{self.fullname}"

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})
