from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_dutyschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeterReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meter_type', models.CharField(choices=[('water', '水表'), ('electric', '电表')], max_length=10, verbose_name='抄表类型')),
                ('reading_month', models.DateField(verbose_name='抄表月份(当月1号)')),
                ('current_reading', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='本期读数')),
                ('previous_reading', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='上期读数')),
                ('usage', models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='本期用量')),
                ('is_first_reading', models.BooleanField(default=False, verbose_name='是否首次抄录')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('recorded_by', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recorded_meter_readings', to=settings.AUTH_USER_MODEL, verbose_name='抄录人')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meter_readings', to='management.unit', verbose_name='关联单元')),
            ],
            options={
                'verbose_name': '抄表记录',
                'verbose_name_plural': '抄表管理',
                'ordering': ['-reading_month', '-created_at'],
                'unique_together': {('unit', 'meter_type', 'reading_month')},
            },
        ),
    ]
