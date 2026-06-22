from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0009_meterreading'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dutyschedule',
            unique_together={('date', 'staff')},
        ),
    ]
