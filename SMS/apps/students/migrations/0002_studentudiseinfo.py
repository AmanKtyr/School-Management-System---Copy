# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentUDISEInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_udise_student', models.BooleanField(default=True)),
                ('mother_tongue', models.CharField(blank=True, default='58-HINDI-Bhojpuri', max_length=100)),
                ('nationality', models.CharField(blank=True, default='Indian', max_length=50)),
                ('is_indian', models.BooleanField(default=True)),
                ('is_ews', models.BooleanField(default=False)),
                ('is_cwsn', models.BooleanField(default=False)),
                ('is_out_of_school', models.BooleanField(default=False)),
                ('mainstreamed_year', models.CharField(blank=True, default='NA', max_length=10)),
                ('disability_type', models.CharField(blank=True, max_length=100)),
                ('has_disability_certificate', models.BooleanField(default=False)),
                ('disability_percentage', models.IntegerField(default=0)),
                ('alternate_mobile', models.CharField(blank=True, max_length=15)),
                ('blood_group', models.CharField(blank=True, default='Under Investigation', max_length=10)),
                ('admitted_under', models.CharField(blank=True, default='NA', max_length=100)),
                ('sld_screened', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='udise_info', to='students.Student')),
            ],
        ),
    ]
