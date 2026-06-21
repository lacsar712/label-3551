from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Visitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='访客姓名')),
                ('phone', models.CharField(max_length=20, verbose_name='联系电话')),
                ('id_card_last4', models.CharField(max_length=4, verbose_name='身份证后四位')),
                ('visit_reason', models.CharField(max_length=200, verbose_name='来访事由')),
                ('estimated_duration', models.IntegerField(verbose_name='预计停留时长(分钟)')),
                ('estimated_leave_time', models.DateTimeField(verbose_name='预计离开时间')),
                ('actual_leave_time', models.DateTimeField(blank=True, null=True, verbose_name='实际离开时间')),
                ('status', models.CharField(choices=[('visiting', '在访'), ('left', '已离场')], default='visiting', max_length=20, verbose_name='状态')),
                ('register_time', models.DateTimeField(auto_now_add=True, verbose_name='登记时间')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitors', to=settings.AUTH_USER_MODEL, verbose_name='拜访业主')),
                ('register_staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registered_visitors', to=settings.AUTH_USER_MODEL, verbose_name='登记人')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitors', to='management.unit', verbose_name='关联房号')),
            ],
            options={
                'verbose_name': '访客记录',
                'verbose_name_plural': '访客管理',
                'ordering': ['-register_time'],
            },
        ),
    ]
