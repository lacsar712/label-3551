from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '系统管理员'),
        ('staff', '物业工作人员'),
        ('owner', '业主'),
    )
    role = models.CharField("角色", max_length=10, choices=ROLE_CHOICES, default='owner')
    phone = models.CharField("联系电话", max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户管理"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Estate(models.Model):
    name = models.CharField("楼盘名称", max_length=100)
    address = models.CharField("楼盘地址", max_length=255)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "楼盘"
        verbose_name_plural = "楼盘管理"

    def __str__(self):
        return self.name

class Building(models.Model):
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, verbose_name="所属楼盘", related_name="buildings")
    name = models.CharField("楼栋名称", max_length=50)

    class Meta:
        verbose_name = "楼栋"
        verbose_name_plural = "楼栋管理"

    def __str__(self):
        return f"{self.estate.name} - {self.name}"

class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name="所属楼栋", related_name="floors")
    name = models.CharField("楼层名称", max_length=50)

    class Meta:
        verbose_name = "楼层"
        verbose_name_plural = "楼层管理"

    def __str__(self):
        return f"{self.building} - {self.name}"

class Unit(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, verbose_name="所属楼层", related_name="units")
    name = models.CharField("单元名称(房号)", max_length=50)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="所属业主", related_name="properties", limit_choices_to={'role': 'owner'})
    area = models.DecimalField("面积(平米)", max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "单元/房屋"
        verbose_name_plural = "单元/房屋管理"

    def __str__(self):
        return f"{self.floor} - {self.name}"

class Repair(models.Model):
    TYPE_CHOICES = (
        ('water_electric', '水电维修'),
        ('door_window', '门窗维修'),
        ('public', '公共设施'),
        ('other', '其他'),
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="提交业主", related_name="repairs")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="相关房屋")
    fault_type = models.CharField("故障类型", max_length=20, choices=TYPE_CHOICES)
    location = models.CharField("故障位置", max_length=100)
    description = models.TextField("故障描述")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='pending')
    
    processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="处理人", related_name="handled_repairs", limit_choices_to={'role': 'staff'})
    feedback = models.TextField("物业处理反馈", blank=True, null=True)
    
    submit_time = models.DateTimeField("提交时间", auto_now_add=True)
    update_time = models.DateTimeField("最后更新时间", auto_now=True)

    class Meta:
        verbose_name = "报修单"
        verbose_name_plural = "报修管理"
        ordering = ['-submit_time']

    def __str__(self):
        return f"报修单 #{self.id} - {self.get_fault_type_display()}"


class Fee(models.Model):
    FEE_TYPES = (
        ('property', '物业费'),
        ('water', '水费'),
        ('electric', '电费'),
        ('other', '其他费用'),
    )
    STATUS_CHOICES = (
        ('unpaid', '未支付'),
        ('paid', '已支付'),
    )
    PAYMENT_METHODS = (
        ('wechat', '微信'),
        ('alipay', '支付宝'),
        ('bank', '银行转账'),
        ('cash', '现金'),
    )
    
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="相关房屋", related_name="fees")
    fee_type = models.CharField("费用类型", max_length=20, choices=FEE_TYPES)
    amount = models.DecimalField("金额", max_digits=10, decimal_places=2)
    generated_date = models.DateField("生成日期", auto_now_add=True)
    due_date = models.DateField("截止日期")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='unpaid')
    
    payment_date = models.DateField("收款日期", null=True, blank=True)
    payment_method = models.CharField("收款方式", max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    
    class Meta:
        verbose_name = "账单记录"
        verbose_name_plural = "费用管理"
        ordering = ['-generated_date']

    def __str__(self):
        return f"{self.unit} - {self.get_fee_type_display()} - {self.amount}元"

class Visitor(models.Model):
    STATUS_CHOICES = (
        ('visiting', '在访'),
        ('left', '已离场'),
    )
    
    name = models.CharField("访客姓名", max_length=50)
    phone = models.CharField("联系电话", max_length=20)
    id_card_last4 = models.CharField("身份证后四位", max_length=4)
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="拜访业主", related_name="visitors", limit_choices_to={'role': 'owner'})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="关联房号", related_name="visitors")
    
    visit_reason = models.CharField("来访事由", max_length=200)
    estimated_duration = models.IntegerField("预计停留时长(分钟)")
    estimated_leave_time = models.DateTimeField("预计离开时间")
    
    actual_leave_time = models.DateTimeField("实际离开时间", null=True, blank=True)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='visiting')
    
    register_time = models.DateTimeField("登记时间", auto_now_add=True)
    register_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="登记人", related_name="registered_visitors", limit_choices_to={'role__in': ['admin', 'staff']})
    
    class Meta:
        verbose_name = "访客记录"
        verbose_name_plural = "访客管理"
        ordering = ['-register_time']
    
    def __str__(self):
        return f"{self.name} - 拜访{self.owner.username}"


class Announcement(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('published', '已发布'),
        ('withdrawn', '已撤回'),
    )

    title = models.CharField("公告标题", max_length=200)
    content = models.TextField("公告正文(富文本)")
    is_pinned = models.BooleanField("是否置顶", default=False)
    effective_start_date = models.DateField("生效开始日期")
    effective_end_date = models.DateField("生效结束日期")

    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='draft')
    publisher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="发布人",
        related_name="published_announcements",
        limit_choices_to={'role__in': ['admin', 'staff']}
    )

    publish_time = models.DateTimeField("发布时间", null=True, blank=True)
    withdraw_time = models.DateTimeField("撤回时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "社区公告"
        verbose_name_plural = "社区公告管理"
        ordering = ['-is_pinned', '-publish_time', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_effective(self):
        from django.utils import timezone
        today = timezone.localdate()
        if self.status != 'published':
            return False
        return self.effective_start_date <= today <= self.effective_end_date

    @property
    def is_expired(self):
        from django.utils import timezone
        today = timezone.localdate()
        return today > self.effective_end_date

class ComplaintSuggestion(models.Model):
    TYPE_CHOICES = (
        ('complaint', '投诉'),
        ('suggestion', '建议'),
        ('inquiry', '咨询'),
    )
    STATUS_CHOICES = (
        ('pending', '待回复'),
        ('replied', '已回复'),
        ('closed', '已关闭'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="提交业主", related_name="complaints")
    cs_type = models.CharField("类型", max_length=20, choices=TYPE_CHOICES)
    title = models.CharField("标题", max_length=200)
    description = models.TextField("详细描述")
    is_anonymous = models.BooleanField("匿名提交", default=False)
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField("提交时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "投诉建议"
        verbose_name_plural = "投诉建议管理"
        ordering = ['-created_at']

    def __str__(self):
        display_name = "匿名用户" if self.is_anonymous else self.owner.username
        return f"#{self.id} [{self.get_cs_type_display()}] {self.title} - {display_name}"


class ComplaintReply(models.Model):
    complaint = models.ForeignKey(ComplaintSuggestion, on_delete=models.CASCADE, verbose_name="关联工单", related_name="replies")
    replier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="回复人", related_name="complaint_replies")
    content = models.TextField("回复内容")
    created_at = models.DateTimeField("回复时间", auto_now_add=True)

    class Meta:
        verbose_name = "投诉建议回复"
        verbose_name_plural = "投诉建议回复管理"
        ordering = ['created_at']

    def __str__(self):
        return f"回复 #{self.complaint.id} - {self.replier}"

    @property
    def replier_display(self):
        if self.replier and self.replier.role in ['admin', 'staff']:
            return f"物业客服 {self.replier.username}"
        if self.complaint.is_anonymous:
            return "匿名业主"
        return self.replier.username if self.replier else "未知"


class ParkingSpot(models.Model):
    TYPE_CHOICES = (
        ('property', '产权'),
        ('rental', '租赁'),
        ('temporary', '临时'),
    )

    spot_number = models.CharField("车位编号", max_length=50)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, verbose_name="所属楼盘", related_name="parking_spots")
    area = models.CharField("所在区域", max_length=100, blank=True, null=True)
    spot_type = models.CharField("车位类型", max_length=20, choices=TYPE_CHOICES, default='rental')
    monthly_fee = models.DecimalField("月租金额", max_digits=10, decimal_places=2, default=0.00)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="绑定业主", related_name="parking_spots", limit_choices_to={'role': 'owner'})
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联单元", related_name="parking_spots")

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "车位"
        verbose_name_plural = "车位管理"
        ordering = ['estate', 'spot_number']
        unique_together = ['estate', 'spot_number']

    def __str__(self):
        return f"{self.estate.name} - {self.spot_number}"

    @property
    def is_bound(self):
        return self.owner is not None

    @property
    def status_text(self):
        return "已绑定" if self.is_bound else "未绑定"


class CommunityActivity(models.Model):
    title = models.CharField("活动名称", max_length=200)
    location = models.CharField("活动地点", max_length=255)
    start_time = models.DateTimeField("开始时间")
    end_time = models.DateTimeField("结束时间")
    max_participants = models.PositiveIntegerField("人数上限", default=50)
    registration_deadline = models.DateTimeField("报名截止时间")
    description = models.TextField("活动简介", blank=True, default='')
    notes = models.TextField("注意事项", blank=True, default='')

    publisher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="发布人",
        related_name="published_activities",
        limit_choices_to={'role__in': ['admin', 'staff']}
    )

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "社区活动"
        verbose_name_plural = "社区活动管理"
        ordering = ['-start_time']

    def __str__(self):
        return self.title

    @property
    def is_full(self):
        return self.registrations.count() >= self.max_participants

    @property
    def remaining_slots(self):
        return max(0, self.max_participants - self.registrations.count())

    @property
    def is_registration_open(self):
        from django.utils import timezone
        now = timezone.now()
        return now <= self.registration_deadline and not self.is_full

    @property
    def is_ended(self):
        from django.utils import timezone
        return timezone.now() > self.end_time


class ActivityRegistration(models.Model):
    activity = models.ForeignKey(CommunityActivity, on_delete=models.CASCADE, verbose_name="所属活动", related_name="registrations")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="报名业主", related_name="activity_registrations", limit_choices_to={'role': 'owner'})

    registered_at = models.DateTimeField("报名时间", auto_now_add=True)

    class Meta:
        verbose_name = "活动报名"
        verbose_name_plural = "活动报名管理"
        unique_together = ['activity', 'owner']
        ordering = ['registered_at']

    def __str__(self):
        return f"{self.owner.username} - {self.activity.title}"


class Package(models.Model):
    STATUS_CHOICES = (
        ('pending', '待领取'),
        ('picked_up', '已领取'),
    )

    SIZE_CHOICES = (
        ('small', '小件'),
        ('medium', '中件'),
        ('large', '大件'),
        ('extra_large', '超大件'),
    )

    COURIER_CHOICES = (
        ('sf', '顺丰速运'),
        ('jd', '京东物流'),
        ('zt', '中通快递'),
        ('yt', '圆通速递'),
        ('yd', '韵达快递'),
        ('ems', 'EMS'),
        ('db', '德邦快递'),
        ('sto', '申通快递'),
        ('other', '其他'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="收件业主", related_name="packages", limit_choices_to={'role': 'owner'})
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="关联房号", related_name="packages")
    courier_company = models.CharField("快递公司", max_length=20, choices=COURIER_CHOICES)
    tracking_last4 = models.CharField("单号后四位", max_length=4)
    package_size = models.CharField("包裹规格", max_length=20, choices=SIZE_CHOICES, default='medium')
    storage_location = models.CharField("存放位置", max_length=100)
    arrival_time = models.DateTimeField("到达时间", auto_now_add=True)
    remarks = models.TextField("备注", blank=True, null=True)

    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_time = models.DateTimeField("领取时间", null=True, blank=True)
    handler = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="经办人", related_name="handled_packages", limit_choices_to={'role__in': ['admin', 'staff']})

    register_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="登记人", related_name="registered_packages", limit_choices_to={'role__in': ['admin', 'staff']})

    class Meta:
        verbose_name = "快递包裹"
        verbose_name_plural = "快递代收管理"
        ordering = ['-arrival_time']

    def __str__(self):
        return f"{self.get_courier_company_display()} - {self.tracking_last4} - {self.owner.username}"

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.status == 'picked_up':
            return False
        now = timezone.now()
        delta = now - self.arrival_time
        return delta.days >= 7

    @property
    def days_pending(self):
        from django.utils import timezone
        if self.status == 'picked_up':
            return 0
        now = timezone.now()
        delta = now - self.arrival_time
        return delta.days


class Equipment(models.Model):
    name = models.CharField("设备名称", max_length=200)
    installation_location = models.CharField("安装位置", max_length=255)
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, verbose_name="所属楼盘", related_name="equipments")
    brand_model = models.CharField("品牌型号", max_length=200, blank=True, null=True)
    installation_date = models.DateField("安装日期", blank=True, null=True)
    warranty_period = models.DateField("质保期限", blank=True, null=True)
    next_maintenance_date = models.DateField("下次维保日期")
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="责任人",
        related_name="responsible_equipments",
        limit_choices_to={'role__in': ['admin', 'staff']}
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "设备设施"
        verbose_name_plural = "设备设施台账"
        ordering = ['next_maintenance_date']

    def __str__(self):
        return f"{self.name} - {self.estate.name}"

    @property
    def is_maintenance_due_soon(self):
        from django.utils import timezone
        today = timezone.localdate()
        delta = self.next_maintenance_date - today
        return 0 <= delta.days <= 30

    @property
    def is_maintenance_overdue(self):
        from django.utils import timezone
        today = timezone.localdate()
        return self.next_maintenance_date < today

    @property
    def days_until_maintenance(self):
        from django.utils import timezone
        today = timezone.localdate()
        delta = self.next_maintenance_date - today
        return delta.days

    @property
    def warranty_status(self):
        from django.utils import timezone
        if not self.warranty_period:
            return "unknown"
        today = timezone.localdate()
        if self.warranty_period < today:
            return "expired"
        delta = self.warranty_period - today
        if delta.days <= 90:
            return "expiring_soon"
        return "valid"


class DutySchedule(models.Model):
    SHIFT_CHOICES = (
        ('morning', '早班'),
        ('afternoon', '中班'),
        ('evening', '晚班'),
    )

    date = models.DateField("值班日期")
    shift = models.CharField("班次", max_length=20, choices=SHIFT_CHOICES)
    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="值班人员",
        related_name="duty_schedules",
        limit_choices_to={'role__in': ['admin', 'staff']}
    )
    remarks = models.TextField("备注", blank=True, default='')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="创建人",
        related_name="created_duty_schedules"
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "值班排班"
        verbose_name_plural = "值班排班管理"
        unique_together = ['date', 'shift', 'staff']
        ordering = ['date', 'shift']

    def __str__(self):
        return f"{self.date} {self.get_shift_display()} - {self.staff.username}"


class MaintenanceLog(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="关联设备", related_name="maintenance_logs")
    maintenance_date = models.DateField("维保日期")
    content = models.TextField("维保内容")
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="操作人",
        related_name="operated_maintenance_logs",
        limit_choices_to={'role__in': ['admin', 'staff']}
    )
    cost = models.DecimalField("费用(元)", max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField("记录时间", auto_now_add=True)

    class Meta:
        verbose_name = "维保日志"
        verbose_name_plural = "维保日志管理"
        ordering = ['-maintenance_date', '-created_at']

    def __str__(self):
        return f"{self.equipment.name} - {self.maintenance_date}"


class DecorationApplication(models.Model):
    DECORATION_TYPE_CHOICES = (
        ('whole_house', '全屋装修'),
        ('partial', '局部装修'),
        ('demolition', '拆改工程'),
    )

    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '审核通过'),
        ('rejected', '已驳回'),
        ('need_materials', '需补充材料'),
        ('completed', '施工已完成'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="申请业主", related_name="decoration_applications", limit_choices_to={'role': 'owner'})
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="装修单元", related_name="decoration_applications")

    decoration_type = models.CharField("装修类型", max_length=20, choices=DECORATION_TYPE_CHOICES)
    start_date = models.DateField("施工开始日期")
    end_date = models.DateField("施工结束日期")

    construction_company = models.CharField("施工单位名称", max_length=200)
    supervisor_phone = models.CharField("施工负责人电话", max_length=20)
    construction_content = models.TextField("施工内容说明")
    commitment = models.TextField("承诺遵守事项")

    status = models.CharField("审核状态", max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="审核人", related_name="reviewed_decorations", limit_choices_to={'role__in': ['admin', 'staff']})
    review_opinion = models.TextField("审核意见", blank=True, null=True)
    review_time = models.DateTimeField("审核时间", null=True, blank=True)

    created_at = models.DateTimeField("提交时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "装修申请"
        verbose_name_plural = "装修申请管理"
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} {self.get_decoration_type_display()} - {self.unit}"

    @property
    def is_in_progress(self):
        from django.utils import timezone
        if self.status != 'approved':
            return False
        today = timezone.localdate()
        return self.start_date <= today <= self.end_date

    @property
    def is_ending_soon(self):
        from django.utils import timezone
        if not self.is_in_progress:
            return False
        today = timezone.localdate()
        delta = self.end_date - today
        return 0 <= delta.days <= 3

    @property
    def days_until_end(self):
        from django.utils import timezone
        today = timezone.localdate()
        delta = self.end_date - today
        return delta.days


class DecorationReview(models.Model):
    application = models.ForeignKey(DecorationApplication, on_delete=models.CASCADE, verbose_name="关联装修申请", related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="审核人", related_name="decoration_reviews")
    action = models.CharField("审核操作", max_length=20, choices=DecorationApplication.STATUS_CHOICES)
    opinion = models.TextField("审核意见")
    created_at = models.DateTimeField("审核时间", auto_now_add=True)

    class Meta:
        verbose_name = "装修审核记录"
        verbose_name_plural = "装修审核记录管理"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_action_display()} - #{self.application.id}"

    @property
    def reviewer_display(self):
        if self.reviewer and self.reviewer.role in ['admin', 'staff']:
            return f"物业工作人员 {self.reviewer.username}"
        return self.reviewer.username if self.reviewer else "未知"
