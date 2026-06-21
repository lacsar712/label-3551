from django.core.management.base import BaseCommand
from management.models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement, ParkingSpot, ComplaintSuggestion, ComplaintReply, Package, CommunityActivity, ActivityRegistration
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
        
        # 7. 创建车位数据
        ParkingSpot.objects.create(
            spot_number='A001',
            estate=estate,
            area='地下一层A区',
            spot_type='property',
            monthly_fee=0,
            owner=owner1,
            unit=u1
        )
        ParkingSpot.objects.create(
            spot_number='A002',
            estate=estate,
            area='地下一层A区',
            spot_type='rental',
            monthly_fee=300,
            owner=owner2,
            unit=u2
        )
        ParkingSpot.objects.create(
            spot_number='A003',
            estate=estate,
            area='地下一层A区',
            spot_type='rental',
            monthly_fee=300
        )
        ParkingSpot.objects.create(
            spot_number='A004',
            estate=estate,
            area='地下一层A区',
            spot_type='temporary',
            monthly_fee=500
        )
        ParkingSpot.objects.create(
            spot_number='B001',
            estate=estate,
            area='地下二层B区',
            spot_type='property',
            monthly_fee=0
        )
        ParkingSpot.objects.create(
            spot_number='B002',
            estate=estate,
            area='地下二层B区',
            spot_type='rental',
            monthly_fee=280
        )
        
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

        # 8. 创建投诉建议数据
        cs1 = ComplaintSuggestion.objects.create(
            owner=owner1, cs_type='complaint',
            title='楼道灯长期不亮',
            description='1栋1层楼道灯已经坏了将近一个月了，晚上回家非常不方便，存在安全隐患，请尽快维修。',
            is_anonymous=False, status='replied'
        )
        ComplaintReply.objects.create(
            complaint=cs1, replier=staff,
            content='您好，感谢您的反馈！我们已经安排电工师傅于本周三前去维修，届时可能需要短暂停电，敬请谅解。'
        )

        cs2 = ComplaintSuggestion.objects.create(
            owner=owner2, cs_type='suggestion',
            title='建议增设快递柜',
            description='小区目前快递只能放在门卫处，经常丢失或拿错。建议在1栋楼下增设智能快递柜，方便业主取件。',
            is_anonymous=False, status='replied'
        )
        ComplaintReply.objects.create(
            complaint=cs2, replier=staff,
            content='感谢您的建议！物业已经联系了丰巢和速递易两家公司，正在协商安装方案，预计下个月可以落实。'
        )

        cs3 = ComplaintSuggestion.objects.create(
            owner=owner1, cs_type='inquiry',
            title='物业费收费标准咨询',
            description='请问物业费是按什么标准收取的？是否有明细可以查看？另外，空置房屋是否有减免政策？',
            is_anonymous=False, status='pending'
        )

        cs4 = ComplaintSuggestion.objects.create(
            owner=owner2, cs_type='complaint',
            title='凌晨施工噪音扰民',
            description='2栋旁边最近几天凌晨2-3点还有施工噪音，严重影响睡眠。请物业出面协调处理。',
            is_anonymous=True, status='closed'
        )
        ComplaintReply.objects.create(
            complaint=cs4, replier=admin,
            content='经核实，该施工为市政管道抢修工程，已与施工方协调，夜间施工时间调整至晚22点前结束。如有再次扰民，请随时联系我们。'
        )
        ComplaintReply.objects.create(
            complaint=cs4, replier=owner2,
            content='好的，希望后续不再有夜间施工的情况，谢谢处理。'
        )

        # 9. 创建快递代收数据
        now = timezone.now()

        Package.objects.create(
            owner=owner1,
            unit=u1,
            courier_company='sf',
            tracking_last4='1234',
            package_size='medium',
            storage_location='1栋快递柜A区03号',
            arrival_time=now - timedelta(hours=2),
            register_staff=staff,
            remarks='易碎品，请轻拿轻放'
        )

        Package.objects.create(
            owner=owner1,
            unit=u1,
            courier_company='jd',
            tracking_last4='5678',
            package_size='large',
            storage_location='1栋物业前台',
            arrival_time=now - timedelta(days=1),
            register_staff=staff
        )

        Package.objects.create(
            owner=owner2,
            unit=u2,
            courier_company='zt',
            tracking_last4='9012',
            package_size='small',
            storage_location='2栋快递柜B区15号',
            arrival_time=now - timedelta(days=3),
            register_staff=staff
        )

        Package.objects.create(
            owner=owner2,
            unit=u2,
            courier_company='yt',
            tracking_last4='3456',
            package_size='medium',
            storage_location='2栋快递柜B区22号',
            arrival_time=now - timedelta(days=8),
            register_staff=staff,
            status='picked_up',
            pickup_time=now - timedelta(days=6),
            handler=staff
        )

        Package.objects.create(
            owner=owner1,
            unit=u1,
            courier_company='ems',
            tracking_last4='7890',
            package_size='extra_large',
            storage_location='1栋物业大件存放区',
            arrival_time=now - timedelta(days=10),
            register_staff=staff,
            remarks='大件包裹，请业主安排人手'
        )

        self.stdout.write(self.style.SUCCESS("快递代收数据生成完成！"))

        # 10. 创建社区活动数据
        now = timezone.now()

        act1 = CommunityActivity.objects.create(
            title='社区亲子运动会',
            location='小区中心广场',
            start_time=now + timedelta(days=7, hours=9),
            end_time=now + timedelta(days=7, hours=12),
            max_participants=30,
            registration_deadline=now + timedelta(days=5, hours=18),
            description='为增进邻里感情，丰富社区文化生活，特举办亲子趣味运动会。活动设有亲子接力赛、拔河比赛、趣味投篮等多个项目，欢迎家长带着孩子一起来参加！',
            notes='1. 请穿着运动服和运动鞋\n2. 自带饮用水和毛巾\n3. 6岁以下儿童需家长全程陪同\n4. 如遇雨天活动顺延',
            publisher=admin
        )

        act2 = CommunityActivity.objects.create(
            title='消防安全知识讲座',
            location='物业服务中心二楼会议室',
            start_time=now + timedelta(days=10, hours=14),
            end_time=now + timedelta(days=10, hours=16),
            max_participants=50,
            registration_deadline=now + timedelta(days=8, hours=18),
            description='邀请消防大队专业教官为业主讲解家庭消防安全知识，包括火灾预防、灭火器使用、逃生自救等实用技能。现场还有实操演练环节。',
            notes='1. 讲座免费参加\n2. 请提前15分钟入场\n3. 现场提供灭火器实操体验',
            publisher=staff
        )

        act3 = CommunityActivity.objects.create(
            title='社区跳蚤市场',
            location='小区东门花园',
            start_time=now + timedelta(days=14, hours=10),
            end_time=now + timedelta(days=14, hours=16),
            max_participants=20,
            registration_deadline=now + timedelta(days=12, hours=20),
            description='闲置物品交换和义卖活动，业主可以申请摊位出售或交换闲置物品，培养环保节约意识，促进邻里交流。义卖所得将捐赠社区公益基金。',
            notes='1. 每户限申请一个摊位\n2. 摊位免费，需自备摆摊用具\n3. 禁止售卖食品和违禁品\n4. 活动结束后请清理摊位',
            publisher=staff
        )

        ActivityRegistration.objects.create(activity=act1, owner=owner1)
        ActivityRegistration.objects.create(activity=act2, owner=owner1)
        ActivityRegistration.objects.create(activity=act2, owner=owner2)
        ActivityRegistration.objects.create(activity=act3, owner=owner2)

        CommunityActivity.objects.create(
            title='春季植树节活动',
            location='小区绿化带',
            start_time=now - timedelta(days=30, hours=9),
            end_time=now - timedelta(days=30, hours=12),
            max_participants=20,
            registration_deadline=now - timedelta(days=32, hours=18),
            description='春季绿化植树活动，业主可认领树苗在小区绿化带种植。',
            notes='请穿着耐脏衣物，物业提供工具和树苗。',
            publisher=admin
        )

        self.stdout.write(self.style.SUCCESS("社区活动数据生成完成！"))

