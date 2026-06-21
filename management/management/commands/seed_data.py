from django.core.management.base import BaseCommand
from management.models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement
from datetime import date, timedelta, datetime
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        if Estate.objects.exists():
            self.stdout.write(self.style.SUCCESS("Database is already seeded."))
            return

        self.stdout.write("Seeding database...")

        # 1. 创建管理人员和业主
        admin = User.objects.filter(username='admin').first()
        if not admin:
            admin = User.objects.create_superuser('admin', 'admin@example.com', '123456', role='admin')
            
        staff = User.objects.create_user('staff', 'staff@example.com', '123456', role='staff', phone='13800138000')
        owner1 = User.objects.create_user('owner1', 'owner1@example.com', '123456', role='owner', phone='13900139000')
        owner2 = User.objects.create_user('owner2', 'owner2@example.com', '123456', role='owner', phone='13700137000')

        # 2. 创建楼盘结构
        estate = Estate.objects.create(name='翠湖天地', address='市中心湖滨路1号')
        b1 = Building.objects.create(estate=estate, name='1栋')
        b2 = Building.objects.create(estate=estate, name='2栋')
        
        f1 = Floor.objects.create(building=b1, name='1层')
        f2 = Floor.objects.create(building=b1, name='2层')
        
        u1 = Unit.objects.create(floor=f1, name='101室', owner=owner1, area=120.5)
        u2 = Unit.objects.create(floor=f1, name='102室', owner=owner2, area=89.0)
        u3 = Unit.objects.create(floor=f2, name='201室', area=145.0) # 未卖出
        
        # 3. 创建报修数据
        Repair.objects.create(
            owner=owner1, unit=u1, fault_type='water_electric',
            location='主卧卫生间', description='水管漏水严重',
            status='processing', processor=staff
        )
        Repair.objects.create(
            owner=owner2, unit=u2, fault_type='door_window',
            location='客厅窗户', description='刮风时有异响'
        )
        
        # 4. 创建费用数据
        today = date.today()
        Fee.objects.create(
            unit=u1, fee_type='property', amount=120.5 * 3.5,
            due_date=today + timedelta(days=15), status='unpaid'
        )
        Fee.objects.create(
            unit=u2, fee_type='water', amount=85.0,
            due_date=today - timedelta(days=5), status='paid',
            payment_date=today - timedelta(days=10), payment_method='wechat'
        )
        
        # 5. 创建访客数据
        now = datetime.now()
        Visitor.objects.create(
            name='张三', phone='13812345678', id_card_last4='1234',
            owner=owner1, unit=u1, visit_reason='亲友拜访',
            estimated_duration=120, estimated_leave_time=now + timedelta(hours=2),
            register_staff=staff
        )
        Visitor.objects.create(
            name='李四', phone='13987654321', id_card_last4='5678',
            owner=owner2, unit=u2, visit_reason='快递配送',
            estimated_duration=30, estimated_leave_time=now + timedelta(minutes=30),
            register_staff=staff
        )
        Visitor.objects.create(
            name='王五', phone='13611112222', id_card_last4='9012',
            owner=owner1, unit=u1, visit_reason='家政服务',
            estimated_duration=180, estimated_leave_time=now + timedelta(hours=3),
            actual_leave_time=now + timedelta(hours=2, minutes=30),
            status='left', register_staff=staff
        )

        # 6. 创建公告数据
        today = timezone.localdate()
        Announcement.objects.create(
            title='关于小区电梯年度维保的重要通知',
            content='<h3>尊敬的各位业主：</h3><p>您好！为确保电梯安全运行，物业将于<strong>本周六（' + (today + timedelta(days=5)).strftime('%m月%d日') + '）</strong>对小区所有电梯进行年度维护保养。</p><p>维保时间：上午 8:00 - 下午 18:00</p><p>维保期间电梯将分批暂停使用，每栋楼预计影响时间约 2-3 小时，请各位业主提前做好出行安排。</p><p>如有紧急情况，请拨打物业服务热线：400-888-8888</p><p>感谢您的理解与配合！</p><p style="text-align:right;">物业管理处</p><p style="text-align:right;">' + today.strftime('%Y年%m月%d日') + '</p>',
            is_pinned=True,
            effective_start_date=today,
            effective_end_date=today + timedelta(days=10),
            status='published',
            publisher=admin,
            publish_time=timezone.now()
        )
        Announcement.objects.create(
            title='垃圾分类新规提醒',
            content='<h3>各位业主：</h3><p>根据最新《城市生活垃圾管理条例》，自下月起，小区将严格执行垃圾分类投放。</p><ul><li>可回收物：纸类、塑料、金属、玻璃等</li><li>有害垃圾：电池、灯管、药品等</li><li>厨余垃圾：剩菜剩饭、果皮等</li><li>其他垃圾：除上述以外的生活垃圾</li></ul><p>请各位业主积极配合，共同维护美好家园环境。</p>',
            is_pinned=True,
            effective_start_date=today - timedelta(days=2),
            effective_end_date=today + timedelta(days=30),
            status='published',
            publisher=staff,
            publish_time=timezone.now() - timedelta(days=2)
        )
        Announcement.objects.create(
            title='夏季高温安全用电提示',
            content='<h3>温馨提示</h3><p>夏季高温来临，用电量激增，请注意以下安全用电事项：</p><ol><li>避免同时使用多个大功率电器</li><li>定期检查家中线路是否老化</li><li>外出时请关闭不必要的电器电源</li><li>如遇停电或故障，请及时联系物业</li></ol><p>物业服务热线：400-888-8888</p>',
            is_pinned=False,
            effective_start_date=today - timedelta(days=1),
            effective_end_date=today + timedelta(days=20),
            status='published',
            publisher=staff,
            publish_time=timezone.now() - timedelta(days=1)
        )
        Announcement.objects.create(
            title='小区绿化养护通知',
            content='<p>各位业主：</p><p>物业将于下周对小区绿化带进行修剪、施肥和病虫害防治工作。届时可能会有园林机械作业噪音，敬请谅解。</p><p>养护期间请照看好老人和儿童，远离作业区域。</p>',
            is_pinned=False,
            effective_start_date=today + timedelta(days=3),
            effective_end_date=today + timedelta(days=15),
            status='published',
            publisher=staff,
            publish_time=timezone.now()
        )
        Announcement.objects.create(
            title='关于举办社区中秋晚会的通知（草稿）',
            content='<p>各位业主：</p><p>为丰富社区文化生活，增进邻里感情，物业拟于中秋节前夕举办社区中秋晚会。</p><p>活动内容：文艺表演、互动游戏、抽奖活动</p><p>（此公告为草稿，待完善后发布）</p>',
            is_pinned=False,
            effective_start_date=today + timedelta(days=30),
            effective_end_date=today + timedelta(days=45),
            status='draft',
            publisher=admin
        )
        Announcement.objects.create(
            title='春节期间物业服务安排',
            content='<p>各位业主：</p><p>2025年春节期间物业服务安排如下：</p><p>（此公告已过期）</p>',
            is_pinned=False,
            effective_start_date=today - timedelta(days=180),
            effective_end_date=today - timedelta(days=160),
            status='published',
            publisher=admin,
            publish_time=timezone.now() - timedelta(days=180)
        )
        
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

