from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_package'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='活动名称')),
                ('location', models.CharField(max_length=255, verbose_name='活动地点')),
                ('start_time', models.DateTimeField(verbose_name='开始时间')),
                ('end_time', models.DateTimeField(verbose_name='结束时间')),
                ('max_participants', models.PositiveIntegerField(default=50, verbose_name='人数上限')),
                ('registration_deadline', models.DateTimeField(verbose_name='报名截止时间')),
                ('description', models.TextField(blank=True, default='', verbose_name='活动简介')),
                ('notes', models.TextField(blank=True, default='', verbose_name='注意事项')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='published_activities', limit_choices_to={'role__in': ['admin', 'staff']}, to=settings.AUTH_USER_MODEL, verbose_name='发布人')),
            ],
            options={
                'verbose_name': '社区活动',
                'verbose_name_plural': '社区活动管理',
                'ordering': ['-start_time'],
            },
        ),
        migrations.CreateModel(
            name='ActivityRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registered_at', models.DateTimeField(auto_now_add=True, verbose_name='报名时间')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='management.communityactivity', verbose_name='所属活动')),
                ('owner', models.ForeignKey(limit_choices_to={'role': 'owner'}, on_delete=django.db.models.deletion.CASCADE, related_name='activity_registrations', to=settings.AUTH_USER_MODEL, verbose_name='报名业主')),
            ],
            options={
                'verbose_name': '活动报名',
                'verbose_name_plural': '活动报名管理',
                'ordering': ['registered_at'],
                'unique_together': {('activity', 'owner')},
            },
        ),
    ]
