from django.db import migrations
import random

def generate_reg_number(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    for student in Student.objects.all():
        if not student.registration_number:
            year_suffix = str(student.date_of_admission.year)[-2:]
            unique_number = str(random.randint(1000, 9999))
            current_class = student.current_class.name if student.current_class else "00"
            student.registration_number = f"{year_suffix}{current_class}{unique_number}"
            student.save()

def reverse_func(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    Student.objects.all().update(registration_number=None)

class Migration(migrations.Migration):
    dependencies = [
        ('students', '0025_student_registration_number'),
    ]

    operations = [
        migrations.RunPython(generate_reg_number, reverse_func),
    ]