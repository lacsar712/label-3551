from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_alter_package_handler_alter_package_owner_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='arrival_time',
            field=models.DateTimeField(default=timezone.now, verbose_name='到达时间'),
        ),
    ]
