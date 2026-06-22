from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_dutyschedule'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='dutyschedule',
            unique_together={('date', 'staff')},
        ),
    ]
