from django.core.management.base import BaseCommand
from management.models import User, Estate, Building, Floor, Unit, Repair, Fee
from datetime import date, timedelta
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
        
        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

