from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('super_admin', '0004_userprofile_bio_userprofile_designation_and_more'),
        ('corecode', '0017_previous_migration'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='classsubject',
            unique_together={('field1', 'field2')},
        ),
    ]