from django.db import migrations, models
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

class Migration(migrations.Migration):
    dependencies = [
        ('students', '0024_alter_student_father_mobile_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='registration_number',
            field=models.CharField(blank=True, max_length=200, null=True, unique=True),
        ),
        migrations.RunPython(generate_reg_number),
    ]

