from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_communityactivity_activityregistration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='设备名称')),
                ('installation_location', models.CharField(max_length=255, verbose_name='安装位置')),
                ('brand_model', models.CharField(blank=True, max_length=200, null=True, verbose_name='品牌型号')),
                ('installation_date', models.DateField(blank=True, null=True, verbose_name='安装日期')),
                ('warranty_period', models.DateField(blank=True, null=True, verbose_name='质保期限')),
                ('next_maintenance_date', models.DateField(verbose_name='下次维保日期')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='equipments', to='management.estate', verbose_name='所属楼盘')),
                ('responsible_person', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='responsible_equipments', to=settings.AUTH_USER_MODEL, verbose_name='责任人')),
            ],
            options={
                'verbose_name': '设备设施',
                'verbose_name_plural': '设备设施台账',
                'ordering': ['next_maintenance_date'],
            },
        ),
        migrations.CreateModel(
            name='MaintenanceLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maintenance_date', models.DateField(verbose_name='维保日期')),
                ('content', models.TextField(verbose_name='维保内容')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)], verbose_name='费用(元)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='记录时间')),
                ('equipment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='maintenance_logs', to='management.equipment', verbose_name='关联设备')),
                ('operator', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='operated_maintenance_logs', to=settings.AUTH_USER_MODEL, verbose_name='操作人')),
            ],
            options={
                'verbose_name': '维保日志',
                'verbose_name_plural': '维保日志管理',
                'ordering': ['-maintenance_date', '-created_at'],
            },
        ),
    ]
