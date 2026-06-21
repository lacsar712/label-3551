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
