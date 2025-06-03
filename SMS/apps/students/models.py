from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
import random
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Sum, Max

class Student(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]

    GENDER_CHOICES = [("male", "Male"), ("female", "Female")]

    category = [("N/A", "N/A"),("Gen", "Gen"), ("OBC", "OBC"), ("SC/ST", "SC/ST"), ("Other", "Other")]

    current_status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="active"
    )
    registration_number = models.CharField(max_length=200, unique=True, null=True, blank=True)
    fullname = models.CharField(max_length=200)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    category = models.CharField(max_length=10, choices=category, default="N/A")

# Aadhaar number validator (must be 12 digits)
    aadhar_validator = RegexValidator(
    regex=r'^\d{12}$',
    message="Aadhaar number must be exactly 12 digits.",
    code='invalid_aadhar'
    )
    aadhar = models.CharField(validators=[aadhar_validator], max_length=12, blank=True)



    date_of_birth = models.DateField(default=timezone.now)
    current_class = models.ForeignKey(
        'corecode.StudentClass',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    section = models.CharField(max_length=10, blank=True)
    date_of_admission = models.DateField(default=timezone.now)

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,15}$", message="Entered mobile number isn't in a right format!"
    )
    mobile_number = models.CharField(
        validators=[mobile_num_regex], max_length=13, blank=True
    )
    email_id = models.EmailField(max_length=254, blank=True)

    Father_name = models.CharField(max_length=255, null=False, blank=False)

    Father_mobile_number = models.CharField( validators=[mobile_num_regex] ,max_length=15,)
    Father_aadhar = models.CharField(validators=[aadhar_validator], max_length=12, blank=True)
    Mother_name = models.CharField(max_length=255, null=True, blank=True)


    address = models.TextField(blank=True)
    others = models.TextField(blank=True)
    passport = models.ImageField(blank=True, upload_to="students/passports/")
    # Barcode Field
    # barcode_image = models.ImageField(upload_to="students/barcodes/", blank=True, null=True)



    def generate_registration_number(self):
        """Generate sequential registration number based on class and section"""
        if not self.registration_number:
            # Get year suffix (last 2 digits of admission year)
            year_suffix = str(self.date_of_admission.year)[-2:]

            # Get class name
            current_class = self.current_class.name if self.current_class else "00"

            # Get section (default to 'A' if empty)
            section = self.section if self.section else "A"

            # Find the highest number for this class and section
            class_section_students = Student.objects.filter(
                current_class=self.current_class,
                section=section
            )

            # Extract the sequence number from existing registration numbers
            max_number = 0
            for student in class_section_students:
                if student.registration_number and len(student.registration_number) >= 3:
                    try:
                        # Try to extract the sequence number from the end of the registration number
                        seq_number = int(student.registration_number[-3:])
                        if seq_number > max_number:
                            max_number = seq_number
                    except (ValueError, IndexError):
                        pass

            # Generate the next sequence number (1-200 range)
            next_number = max_number + 1
            if next_number > 200:
                next_number = 1  # Reset if exceeds 200

            # Format the sequence number to be 3 digits (e.g., 001, 012, 123)
            formatted_number = f"{next_number:03d}"

            # Create the registration number in format: YYClassSection###
            # Example: 25 + 11 + A + 001 = 2511A001
            self.registration_number = f"{year_suffix}{current_class}{section}{formatted_number}"

        return self.registration_number

    def save(self, *args, **kwargs):
        if not self.registration_number:
            self.registration_number = self.generate_registration_number()
        super().save(*args, **kwargs)

    def get_total_fee(self):
        """Calculate total fee for the student"""
        from apps.fees.models import FeePayment
        return FeePayment.objects.filter(
            student=self,
            status='Paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

    def get_paid_fee(self):
        """Calculate total paid fee for the student"""
        from apps.fees.models import FeePayment
        return FeePayment.objects.filter(
            student=self,
            status='Paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

    def get_due_fee(self):
        """Calculate due fee for the student"""
        return self.get_total_fee() - self.get_paid_fee()

    class Meta:
        ordering = ["fullname",]

    def __str__(self):
        return f"{self.fullname} "

    def get_absolute_url(self):
        return reverse("student-detail", kwargs={"pk": self.pk})


class StudentBulkUpload(models.Model):
    date_uploaded = models.DateTimeField(auto_now=True)
    csv_file = models.FileField(upload_to="students/bulkupload/")


class StudentUDISEInfo(models.Model):
    """Model for storing UDISE+ specific information for students"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='udise_info')

    # Flag to indicate if student was admitted through UDISE form
    is_udise_student = models.BooleanField(default=True)

    # UDISE specific fields
    mother_tongue = models.CharField(max_length=100, blank=True, default="58-HINDI-Bhojpuri")
    nationality = models.CharField(max_length=50, blank=True, default="Indian")
    is_indian = models.BooleanField(default=True)

    # EWS and other status fields
    is_ews = models.BooleanField(default=False)
    is_cwsn = models.BooleanField(default=False)
    is_out_of_school = models.BooleanField(default=False)
    mainstreamed_year = models.CharField(max_length=10, blank=True, default="NA")

    # Disability related fields
    disability_type = models.CharField(max_length=100, blank=True)
    has_disability_certificate = models.BooleanField(default=False)
    disability_percentage = models.IntegerField(default=0)

    # Additional contact information
    alternate_mobile = models.CharField(max_length=15, blank=True)

    # Health information
    blood_group = models.CharField(max_length=10, blank=True, default="Under Investigation")

    # Enrollment details
    admitted_under = models.CharField(max_length=100, blank=True, default="NA")

    # Facility details
    sld_screened = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"UDISE Info for {self.student.fullname}"


class StudentDocument(models.Model):
    """Model for storing student documents"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')

    # Document files with their numbers
    aadhar_card = models.FileField(upload_to="students/documents/aadhar/", blank=True, null=True)
    aadhar_card_number = models.CharField(max_length=50, blank=True)

    birth_certificate = models.FileField(upload_to="students/documents/birth/", blank=True, null=True)
    birth_certificate_number = models.CharField(max_length=50, blank=True)

    address_proof = models.FileField(upload_to="students/documents/address/", blank=True, null=True)
    address_proof_number = models.CharField(max_length=50, blank=True)

    parent_photo = models.FileField(upload_to="students/documents/parent_photo/", blank=True, null=True)
    parent_photo_number = models.CharField(max_length=50, blank=True)

    parent_id_proof = models.FileField(upload_to="students/documents/parent_id/", blank=True, null=True)
    parent_id_proof_number = models.CharField(max_length=50, blank=True)

    previous_marksheet = models.FileField(upload_to="students/documents/marksheet/", blank=True, null=True)
    previous_marksheet_number = models.CharField(max_length=50, blank=True)

    transfer_certificate = models.FileField(upload_to="students/documents/transfer/", blank=True, null=True)
    transfer_certificate_number = models.CharField(max_length=50, blank=True)

    character_certificate = models.FileField(upload_to="students/documents/character/", blank=True, null=True)
    character_certificate_number = models.CharField(max_length=50, blank=True)

    caste_certificate = models.FileField(upload_to="students/documents/caste/", blank=True, null=True)
    caste_certificate_number = models.CharField(max_length=50, blank=True)

    medical_certificate = models.FileField(upload_to="students/documents/medical/", blank=True, null=True)
    medical_certificate_number = models.CharField(max_length=50, blank=True)

    other_document = models.FileField(upload_to="students/documents/other/", blank=True, null=True)
    other_document_number = models.CharField(max_length=50, blank=True)

    # Upload timestamps
    date_uploaded = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Documents for {self.student.fullname}"
