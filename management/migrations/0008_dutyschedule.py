from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0007_equipment_maintenancelog'),
    ]

    operations = [
        migrations.CreateModel(
            name='DutySchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='值班日期')),
                ('shift', models.CharField(choices=[('morning', '早班'), ('afternoon', '中班'), ('evening', '晚班')], max_length=20, verbose_name='班次')),
                ('remarks', models.TextField(blank=True, default='', verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_duty_schedules', to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
                ('staff', models.ForeignKey(limit_choices_to={'role__in': ['admin', 'staff']}, on_delete=django.db.models.deletion.CASCADE, related_name='duty_schedules', to=settings.AUTH_USER_MODEL, verbose_name='值班人员')),
            ],
            options={
                'verbose_name': '值班排班',
                'verbose_name_plural': '值班排班管理',
                'ordering': ['date', 'shift'],
                'unique_together': {('date', 'shift', 'staff')},
            },
        ),
    ]
