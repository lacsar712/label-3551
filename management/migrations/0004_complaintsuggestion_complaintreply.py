from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_announcement'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComplaintSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cs_type', models.CharField(choices=[('complaint', '投诉'), ('suggestion', '建议'), ('inquiry', '咨询')], max_length=20, verbose_name='类型')),
                ('title', models.CharField(max_length=200, verbose_name='标题')),
                ('description', models.TextField(verbose_name='详细描述')),
                ('is_anonymous', models.BooleanField(default=False, verbose_name='匿名提交')),
                ('status', models.CharField(choices=[('pending', '待回复'), ('replied', '已回复'), ('closed', '已关闭')], default='pending', max_length=20, verbose_name='状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='提交时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints', to=settings.AUTH_USER_MODEL, verbose_name='提交业主')),
            ],
            options={
                'verbose_name': '投诉建议',
                'verbose_name_plural': '投诉建议管理',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ComplaintReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='回复内容')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='回复时间')),
                ('complaint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='management.complaintsuggestion', verbose_name='关联工单')),
                ('replier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaint_replies', to=settings.AUTH_USER_MODEL, verbose_name='回复人')),
            ],
            options={
                'verbose_name': '投诉建议回复',
                'verbose_name_plural': '投诉建议回复管理',
                'ordering': ['created_at'],
            },
        ),
    ]
