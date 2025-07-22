from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
import random

class Staff(models.Model):
    STATUS = [("active", "Active"), ("inactive", "Inactive")]
    GENDER = [("male", "Male"), ("female", "Female")]

    current_status = models.CharField(max_length=10, choices=STATUS, default="active")
    registration_number = models.CharField(max_length=200, unique=True, null=True, blank=True)
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

    staff_login_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    staff_password = models.CharField(max_length=50, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def generate_registration_number(self):
        """Generate registration number for staff"""
        if self.date_of_registration:
            year_suffix = str(self.date_of_registration.year)[-2:]  # Extract last 2 digits of year
        else:
            year_suffix = "25"  # Default if date_of_registration is missing

        unique_number = str(random.randint(1000, 9999))
        return f"{year_suffix}{unique_number}"

    def generate_staff_login_credentials(self):
        """Generate login ID and password for staff"""
        # Use registration_number as login ID
        if not self.registration_number:
            self.registration_number = self.generate_registration_number()

        # Set login ID as registration_number
        self.staff_login_id = self.registration_number

        # Set password as registration_number + @#12
        self.staff_password = f"{self.registration_number}@#12"

        # Create or update Django User account
        if not self.user:
            # Create new user
            user = User.objects.create_user(
                username=self.staff_login_id,
                password=self.staff_password,
                first_name=self.fullname.split()[0] if self.fullname else '',
                last_name=' '.join(self.fullname.split()[1:]) if len(self.fullname.split()) > 1 else '',
                is_staff=True,  # Allow access to admin if needed
                is_active=True
            )
            self.user = user
        else:
            # Update existing user
            self.user.username = self.staff_login_id
            self.user.set_password(self.staff_password)
            self.user.first_name = self.fullname.split()[0] if self.fullname else ''
            self.user.last_name = ' '.join(self.fullname.split()[1:]) if len(self.fullname.split()) > 1 else ''
            self.user.save()

    def save(self, *args, **kwargs):
        # Generate registration number if not exists
        if not self.registration_number:
            self.registration_number = self.generate_registration_number()

        # Generate login credentials
        if not self.staff_login_id or not self.staff_password:
            self.generate_staff_login_credentials()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fullname}"

    def get_absolute_url(self):
        return reverse("staff-detail", kwargs={"pk": self.pk})
