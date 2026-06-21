from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_complaintsuggestion_complaintreply'),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('courier_company', models.CharField(choices=[('sf', '顺丰速运'), ('jd', '京东物流'), ('zt', '中通快递'), ('yt', '圆通速递'), ('yd', '韵达快递'), ('ems', 'EMS'), ('db', '德邦快递'), ('sto', '申通快递'), ('other', '其他')], max_length=20, verbose_name='快递公司')),
                ('tracking_last4', models.CharField(max_length=4, verbose_name='单号后四位')),
                ('package_size', models.CharField(choices=[('small', '小件'), ('medium', '中件'), ('large', '大件'), ('extra_large', '超大件')], default='medium', max_length=20, verbose_name='包裹规格')),
                ('storage_location', models.CharField(max_length=100, verbose_name='存放位置')),
                ('arrival_time', models.DateTimeField(auto_now_add=True, verbose_name='到达时间')),
                ('remarks', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('status', models.CharField(choices=[('pending', '待领取'), ('picked_up', '已领取')], default='pending', max_length=20, verbose_name='状态')),
                ('pickup_time', models.DateTimeField(blank=True, null=True, verbose_name='领取时间')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packages', to=settings.AUTH_USER_MODEL, verbose_name='收件业主')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='packages', to='management.unit', verbose_name='关联房号')),
                ('handler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handled_packages', to=settings.AUTH_USER_MODEL, verbose_name='经办人')),
                ('register_staff', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registered_packages', to=settings.AUTH_USER_MODEL, verbose_name='登记人')),
            ],
            options={
                'verbose_name': '快递包裹',
                'verbose_name_plural': '快递代收管理',
                'ordering': ['-arrival_time'],
            },
        ),
    ]
