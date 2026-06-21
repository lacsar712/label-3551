from django import forms
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement, ParkingSpot, ComplaintSuggestion, ComplaintReply, Package, CommunityActivity
from django.utils import timezone

class OwnerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class EstateForm(forms.ModelForm):
    class Meta:
        model = Estate
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'
        widgets = {
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class FloorForm(forms.ModelForm):
    class Meta:
        model = Floor
        fields = '__all__'
        widgets = {
            'building': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = '__all__'
        widgets = {
            'floor': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RepairStaffForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['status', 'processor', 'feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'processor': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class RepairOwnerForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['unit', 'fault_type', 'location', 'description']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'fault_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        if owner:
            # 只显示属于当前业主的房产
            self.fields['unit'].queryset = Unit.objects.filter(owner=owner)

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = '__all__'
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'fee_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }

class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['name', 'phone', 'id_card_last4', 'owner', 'unit', 'visit_reason', 'estimated_duration', 'estimated_leave_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'id_card_last4': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '4'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'visit_reason': forms.TextInput(attrs={'class': 'form-control'}),
            'estimated_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'estimated_leave_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.filter(role='owner')
        self.fields['unit'].queryset = Unit.objects.all()
        if not self.instance.pk:
            self.initial['estimated_leave_time'] = (timezone.now() + timezone.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M')
            self.initial['estimated_duration'] = 120

class VisitorLeaveForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['actual_leave_time']
        widgets = {
            'actual_leave_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.actual_leave_time:
            self.initial['actual_leave_time'] = timezone.now().strftime('%Y-%m-%dT%H:%M')


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_pinned', 'effective_start_date', 'effective_end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入公告标题'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': '请输入公告正文，支持HTML富文本内容', 'id': 'id_content'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'effective_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'effective_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            today = timezone.localdate()
            self.initial['effective_start_date'] = today
            self.initial['effective_end_date'] = today + timezone.timedelta(days=30)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('effective_start_date')
        end = cleaned_data.get('effective_end_date')
        if start and end and start > end:
            raise forms.ValidationError("生效开始日期不能晚于结束日期")
        return cleaned_data

class ParkingSpotForm(forms.ModelForm):
    class Meta:
        model = ParkingSpot
        fields = ['spot_number', 'estate', 'area', 'spot_type', 'monthly_fee', 'owner', 'unit']
        widgets = {
            'spot_number': forms.TextInput(attrs={'class': 'form-control'}),
            'estate': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.TextInput(attrs={'class': 'form-control'}),
            'spot_type': forms.Select(attrs={'class': 'form-select'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.filter(role='owner')
        self.fields['unit'].queryset = Unit.objects.all()


class ComplaintSuggestionForm(forms.ModelForm):
    class Meta:
        model = ComplaintSuggestion
        fields = ['cs_type', 'title', 'description', 'is_anonymous']
        widgets = {
            'cs_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入标题'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '请详细描述您的投诉、建议或咨询内容'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ComplaintReplyForm(forms.ModelForm):
    class Meta:
        model = ComplaintReply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入回复内容'}),
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['owner', 'unit', 'courier_company', 'tracking_last4', 'package_size', 'storage_location', 'remarks']
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'courier_company': forms.Select(attrs={'class': 'form-select'}),
            'tracking_last4': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '4', 'placeholder': '请输入单号后四位'}),
            'package_size': forms.Select(attrs={'class': 'form-select'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：1栋快递柜A区03号'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '选填，如易碎品、冷藏等特殊说明'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.filter(role='owner')
        self.fields['unit'].queryset = Unit.objects.all()


class PackagePickupForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['pickup_time']
        widgets = {
            'pickup_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pickup_time:
            self.initial['pickup_time'] = timezone.now().strftime('%Y-%m-%dT%H:%M')


class CommunityActivityForm(forms.ModelForm):
    class Meta:
        model = CommunityActivity
        fields = ['title', 'location', 'start_time', 'end_time', 'max_participants', 'registration_deadline', 'description', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入活动名称'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入活动地点'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'registration_deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': '请输入活动简介'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '请输入注意事项，如：请穿着运动鞋、自带饮用水等'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            now = timezone.now()
            self.initial['start_time'] = (now + timezone.timedelta(days=7)).strftime('%Y-%m-%dT%H:%M')
            self.initial['end_time'] = (now + timezone.timedelta(days=7, hours=3)).strftime('%Y-%m-%dT%H:%M')
            self.initial['registration_deadline'] = (now + timezone.timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        registration_deadline = cleaned_data.get('registration_deadline')
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("结束时间必须晚于开始时间")
        if start_time and registration_deadline and registration_deadline >= start_time:
            raise forms.ValidationError("报名截止时间必须早于活动开始时间")
        return cleaned_data
