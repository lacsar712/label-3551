from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0009_meterreading'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingSpot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spot_number', models.CharField(max_length=50, verbose_name='车位编号')),
                ('area', models.CharField(blank=True, max_length=100, null=True, verbose_name='所在区域')),
                ('spot_type', models.CharField(choices=[('property', '产权'), ('rental', '租赁'), ('temporary', '临时')], default='rental', max_length=20, verbose_name='车位类型')),
                ('monthly_fee', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='月租金额')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('estate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parking_spots', to='management.estate', verbose_name='所属楼盘')),
                ('owner', models.ForeignKey(blank=True, limit_choices_to={'role': 'owner'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parking_spots', to=settings.AUTH_USER_MODEL, verbose_name='绑定业主')),
                ('unit', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parking_spots', to='management.unit', verbose_name='关联单元')),
            ],
            options={
                'verbose_name': '车位',
                'verbose_name_plural': '车位管理',
                'ordering': ['estate', 'spot_number'],
                'unique_together': {('estate', 'spot_number')},
            },
        ),
        migrations.CreateModel(
            name='DecorationApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decoration_type', models.CharField(choices=[('whole_house', '全屋装修'), ('partial', '局部装修'), ('demolition', '拆改工程')], max_length=20, verbose_name='装修类型')),
                ('start_date', models.DateField(verbose_name='施工开始日期')),
                ('end_date', models.DateField(verbose_name='施工结束日期')),
                ('construction_company', models.CharField(max_length=200, verbose_name='施工单位名称')),
                ('supervisor_phone', models.CharField(max_length=20, verbose_name='施工负责人电话')),
                ('construction_content', models.TextField(verbose_name='施工内容说明')),
                ('commitment', models.TextField(verbose_name='承诺遵守事项')),
                ('status', models.CharField(choices=[('pending', '待审核'), ('approved', '审核通过'), ('rejected', '已驳回'), ('need_materials', '需补充材料'), ('completed', '施工已完成')], default='pending', max_length=20, verbose_name='审核状态')),
                ('review_opinion', models.TextField(blank=True, null=True, verbose_name='审核意见')),
                ('review_time', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='提交时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(limit_choices_to={'role': 'owner'}, on_delete=django.db.models.deletion.CASCADE, related_name='decoration_applications', to=settings.AUTH_USER_MODEL, verbose_name='申请业主')),
                ('reviewer', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_decorations', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decoration_applications', to='management.unit', verbose_name='装修单元')),
            ],
            options={
                'verbose_name': '装修申请',
                'verbose_name_plural': '装修申请管理',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DecorationReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('pending', '待审核'), ('approved', '审核通过'), ('rejected', '已驳回'), ('need_materials', '需补充材料'), ('completed', '施工已完成')], max_length=20, verbose_name='审核操作')),
                ('opinion', models.TextField(verbose_name='审核意见')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='审核时间')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='management.decorationapplication', verbose_name='关联装修申请')),
                ('reviewer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='decoration_reviews', to=settings.AUTH_USER_MODEL, verbose_name='审核人')),
            ],
            options={
                'verbose_name': '装修审核记录',
                'verbose_name_plural': '装修审核记录管理',
                'ordering': ['created_at'],
            },
        ),
    ]
