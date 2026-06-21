from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_visitor'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='公告标题')),
                ('content', models.TextField(verbose_name='公告正文(富文本)')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='是否置顶')),
                ('effective_start_date', models.DateField(verbose_name='生效开始日期')),
                ('effective_end_date', models.DateField(verbose_name='生效结束日期')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('published', '已发布'), ('withdrawn', '已撤回')], default='draft', max_length=20, verbose_name='状态')),
                ('publish_time', models.DateTimeField(blank=True, null=True, verbose_name='发布时间')),
                ('withdraw_time', models.DateTimeField(blank=True, null=True, verbose_name='撤回时间')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('publisher', models.ForeignKey(blank=True, limit_choices_to={'role__in': ['admin', 'staff']}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='published_announcements', to=settings.AUTH_USER_MODEL, verbose_name='发布人')),
            ],
            options={
                'verbose_name': '社区公告',
                'verbose_name_plural': '社区公告管理',
                'ordering': ['-is_pinned', '-publish_time', '-created_at'],
            },
        ),
    ]
