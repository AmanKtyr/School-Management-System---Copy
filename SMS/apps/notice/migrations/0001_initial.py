# Generated manually for notice app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('corecode', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NoticeCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#007bff', help_text='Hex color code for category display', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Notice Category',
                'verbose_name_plural': 'Notice Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')], default='draft', max_length=10)),
                ('recipient_type', models.CharField(choices=[('all', 'All Users'), ('students', 'All Students'), ('teachers', 'All Teachers'), ('staff', 'All Staff'), ('class', 'Specific Class'), ('individual', 'Individual Users')], default='all', max_length=15)),
                ('valid_from', models.DateTimeField(default=django.utils.timezone.now)),
                ('valid_until', models.DateTimeField(blank=True, help_text='Leave blank for no expiry', null=True)),
                ('send_email', models.BooleanField(default=False, help_text='Send email notification')),
                ('send_sms', models.BooleanField(default=False, help_text='Send SMS notification')),
                ('is_important', models.BooleanField(default=False, help_text='Mark as important notice')),
                ('attachment', models.FileField(blank=True, null=True, upload_to='notices/attachments/')),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='notice.noticecategory')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_notices', to=settings.AUTH_USER_MODEL)),
                ('target_class', models.ForeignKey(blank=True, help_text="Select class if recipient type is 'Specific Class'", null=True, on_delete=django.db.models.deletion.CASCADE, to='corecode.studentclass')),
            ],
            options={
                'verbose_name': 'Notice',
                'verbose_name_plural': 'Notices',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NoticeRecipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_sent_at', models.DateTimeField(blank=True, null=True)),
                ('sms_sent', models.BooleanField(default=False)),
                ('sms_sent_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('notice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipients', to='notice.notice')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notice Recipient',
                'verbose_name_plural': 'Notice Recipients',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='noticerecipient',
            constraint=models.UniqueConstraint(fields=('notice', 'user'), name='unique_notice_user'),
        ),
    ]
