from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement, ParkingSpot, ComplaintSuggestion, ComplaintReply, Package
from .forms import EstateForm, BuildingForm, FloorForm, UnitForm, OwnerForm, RepairOwnerForm, RepairStaffForm, FeeForm, VisitorForm, VisitorLeaveForm, AnnouncementForm, ParkingSpotForm, ComplaintSuggestionForm, ComplaintReplyForm, PackageForm, PackagePickupForm
from django.views.generic import DetailView
from django.utils import timezone
from datetime import date
import csv
from django.http import HttpResponse

class CustomLoginView(LoginView):
    template_name = 'management/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        print("Login failed! Errors:", form.errors)
        print("Data received:", self.request.POST)
        return super().form_invalid(form)

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in ['admin', 'staff']
        
class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'management/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        if self.request.user.role in ['admin', 'staff']:
            context['estate_count'] = Estate.objects.count()
            context['owner_count'] = User.objects.filter(role='owner').count()
            context['pending_repairs'] = Repair.objects.filter(status='pending').count()
            context['unpaid_fees'] = Fee.objects.filter(status='unpaid').count()
            context['visiting_count'] = Visitor.objects.filter(status='visiting').count()
            context['draft_announcements'] = Announcement.objects.filter(status='draft').count()
            context['pending_complaints'] = ComplaintSuggestion.objects.filter(status='pending').count()
            context['pending_packages'] = Package.objects.filter(status='pending').count()
            context['overdue_packages'] = Package.objects.filter(status='pending', arrival_time__lte=timezone.now() - timezone.timedelta(days=7)).count()
        else:
            context['my_units'] = Unit.objects.filter(owner=self.request.user)
            context['my_parking_spots'] = ParkingSpot.objects.filter(owner=self.request.user)
            context['my_repairs'] = Repair.objects.filter(owner=self.request.user).order_by('-submit_time')[:5]
            context['unpaid_fees'] = Fee.objects.filter(unit__owner=self.request.user, status='unpaid')
            context['today_visitors'] = Visitor.objects.filter(
                owner=self.request.user,
                register_time__date=today
            ).order_by('-register_time')
            context['pinned_announcements'] = Announcement.objects.filter(
                status='published',
                is_pinned=True,
                effective_start_date__lte=today,
                effective_end_date__gte=today
            ).order_by('-publish_time')
            context['recent_announcements'] = Announcement.objects.filter(
                status='published',
                effective_start_date__lte=today,
                effective_end_date__gte=today
            ).order_by('-is_pinned', '-publish_time')[:10]
            context['my_pending_packages'] = Package.objects.filter(
                owner=self.request.user,
                status='pending'
            ).order_by('-arrival_time')
        return context

# --- 楼盘管理 ---
class EstateListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Estate
    template_name = 'management/estate_list.html'
    context_object_name = 'estates'

class EstateCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Estate
    form_class = EstateForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('estate_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增楼盘"
        return context

class EstateUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Estate
    form_class = EstateForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('estate_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改楼盘"
        return context

class EstateDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Estate
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('estate_list')

# --- 楼栋管理 ---
class BuildingListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Building
    template_name = 'management/building_list.html'
    context_object_name = 'buildings'

class BuildingCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('building_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增楼栋"
        return context

class BuildingUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('building_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改楼栋"
        return context

class BuildingDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Building
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('building_list')

# --- 楼层管理 ---
class FloorListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Floor
    template_name = 'management/floor_list.html'
    context_object_name = 'floors'

class FloorCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Floor
    form_class = FloorForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增楼层"
        return context

class FloorUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Floor
    form_class = FloorForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('floor_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改楼层"
        return context

class FloorDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Floor
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('floor_list')

# --- 单元(房屋)管理 ---
class UnitListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Unit
    template_name = 'management/unit_list.html'
    context_object_name = 'units'

class UnitCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('unit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增单元/房屋"
        return context

class UnitUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('unit_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改单元/房屋"
        return context

class UnitDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Unit
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('unit_list')

# --- 业主管理 ---
class OwnerListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'management/owner_list.html'
    context_object_name = 'owners'

    def get_queryset(self):
        return User.objects.filter(role='owner')

class OwnerCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = User
    form_class = OwnerForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('owner_list')

    def form_valid(self, form):
        form.instance.role = 'owner'
        form.instance.set_password('123456') # Default password
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增业主信息 (默认密码123456)"
        return context

class OwnerUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = User
    form_class = OwnerForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('owner_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改业主信息"
        return context

class OwnerDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = User
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('owner_list')

# --- 报修管理 ---
class RepairListView(LoginRequiredMixin, ListView):
    model = Repair
    template_name = 'management/repair_list.html'
    context_object_name = 'repairs'

    def get_queryset(self):
        qs = Repair.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)
            
        # 多条件过滤
        fault_type = self.request.GET.get('fault_type')
        status = self.request.GET.get('status')
        if fault_type:
            qs = qs.filter(fault_type=fault_type)
        if status:
            qs = qs.filter(status=status)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fault_types'] = Repair.TYPE_CHOICES
        context['statuses'] = Repair.STATUS_CHOICES
        return context

class RepairCreateView(LoginRequiredMixin, CreateView):
    model = Repair
    form_class = RepairOwnerForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('repair_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.role == 'owner':
            kwargs['owner'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "报修申请提交成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "提交报修"
        return context

class RepairUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Repair
    form_class = RepairStaffForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('repair_list')

    def form_valid(self, form):
        messages.success(self.request, "处理进度更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "处理报修"
        return context

# --- 费用中心 ---
class FeeListView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = 'management/fee_list.html'
    context_object_name = 'fees'

    def get_queryset(self):
        qs = Fee.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(unit__owner=self.request.user)
            
        # 过滤
        status = self.request.GET.get('status')
        fee_type = self.request.GET.get('fee_type')
        if status:
            qs = qs.filter(status=status)
        if fee_type:
            qs = qs.filter(fee_type=fee_type)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Fee.STATUS_CHOICES
        context['fee_types'] = Fee.FEE_TYPES
        return context

    def get(self, request, *args, **kwargs):
        if 'export' in request.GET and request.user.role in ['admin', 'staff']:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="fee_export.csv"'
            response.write('\xEF\xBB\xBF') # UTF-8 BOM

            writer = csv.writer(response)
            writer.writerow(['费用类型', '关联房屋', '业主', '金额', '状态', '截止日期', '收款日期'])

            for fee in self.get_queryset():
                owner_name = fee.unit.owner.username if fee.unit.owner else '未绑定'
                writer.writerow([
                    fee.get_fee_type_display(),
                    f"{fee.unit.floor.building.estate.name}-{fee.unit.floor.building.name}-{fee.unit.name}",
                    owner_name,
                    fee.amount,
                    fee.get_status_display(),
                    fee.due_date,
                    fee.payment_date or '-'
                ])
            return response
        return super().get(request, *args, **kwargs)

class FeeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Fee
    form_class = FeeForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('fee_list')

    def form_valid(self, form):
        messages.success(self.request, "账单生成成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "生成账单"
        return context

class FeeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Fee
    form_class = FeeForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('fee_list')

    def form_valid(self, form):
        messages.success(self.request, "账单记录更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "修改或收款"
        return context

class FeeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Fee
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('fee_list')

class VisitorListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Visitor
    template_name = 'management/visitor_list.html'
    context_object_name = 'visitors'

    def get_queryset(self):
        qs = Visitor.objects.all()
        
        visit_date = self.request.GET.get('visit_date')
        owner_id = self.request.GET.get('owner')
        status = self.request.GET.get('status')
        
        if visit_date:
            qs = qs.filter(register_time__date=visit_date)
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        if status:
            qs = qs.filter(status=status)
            
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owners'] = User.objects.filter(role='owner')
        context['statuses'] = Visitor.STATUS_CHOICES
        context['current_filters'] = {
            'visit_date': self.request.GET.get('visit_date', ''),
            'owner': self.request.GET.get('owner', ''),
            'status': self.request.GET.get('status', ''),
        }
        return context

class VisitorCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Visitor
    form_class = VisitorForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('visitor_list')

    def form_valid(self, form):
        form.instance.register_staff = self.request.user
        messages.success(self.request, "访客登记成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "访客登记"
        return context

class VisitorDetailView(LoginRequiredMixin, DetailView):
    model = Visitor
    template_name = 'management/visitor_detail.html'
    context_object_name = 'visitor'

    def get_queryset(self):
        qs = Visitor.objects.all()
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)
        return qs

class VisitorLeaveView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Visitor
    form_class = VisitorLeaveForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('visitor_list')

    def form_valid(self, form):
        form.instance.status = 'left'
        messages.success(self.request, "访客已标记离场！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "标记访客离场"
        return context


class AnnouncementListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Announcement
    template_name = 'management/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        tab = self.request.GET.get('tab', 'active')
        today = timezone.localdate()
        qs = Announcement.objects.all()

        status_filter = self.request.GET.get('status')
        search = self.request.GET.get('search')

        if tab == 'active':
            qs = qs.filter(status__in=['draft', 'published', 'withdrawn'])
        elif tab == 'history':
            qs = qs.filter(effective_end_date__lt=today)

        if status_filter:
            qs = qs.filter(status=status_filter)

        if search:
            qs = qs.filter(title__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tab'] = self.request.GET.get('tab', 'active')
        context['statuses'] = Announcement.STATUS_CHOICES
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'search': self.request.GET.get('search', ''),
        }
        context['today'] = timezone.localdate()
        return context


class AnnouncementCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'management/announcement_form.html'
    success_url = reverse_lazy('announcement_list')

    def form_valid(self, form):
        action = self.request.POST.get('action')
        form.instance.publisher = self.request.user

        if action == 'publish':
            form.instance.status = 'published'
            form.instance.publish_time = timezone.now()
            messages.success(self.request, "公告发布成功！")
        else:
            form.instance.status = 'draft'
            messages.success(self.request, "公告已保存为草稿！")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "撰写社区公告"
        context['is_editing'] = False
        return context


class AnnouncementUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'management/announcement_form.html'
    success_url = reverse_lazy('announcement_list')

    def form_valid(self, form):
        action = self.request.POST.get('action')
        form.instance.publisher = self.request.user

        if action == 'publish':
            form.instance.status = 'published'
            if not self.object.publish_time:
                form.instance.publish_time = timezone.now()
            form.instance.withdraw_time = None
            messages.success(self.request, "公告发布成功！")
        elif action == 'withdraw':
            form.instance.status = 'withdrawn'
            form.instance.withdraw_time = timezone.now()
            messages.warning(self.request, "公告已撤回！")
        else:
            if self.object.status == 'published':
                pass
            else:
                form.instance.status = 'draft'
            messages.success(self.request, "公告已保存！")

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑社区公告"
        context['is_editing'] = True
        return context


class AnnouncementDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('announcement_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "公告已删除！")
        return super().delete(request, *args, **kwargs)


class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = 'management/announcement_detail.html'
    context_object_name = 'announcement'

    def get_queryset(self):
        qs = Announcement.objects.all()
        if self.request.user.role == 'owner':
            today = timezone.localdate()
            qs = qs.filter(
                status='published',
                effective_start_date__lte=today,
                effective_end_date__gte=today
            )
        return qs


class AnnouncementPublishView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.status = 'published'
        announcement.publish_time = timezone.now()
        announcement.withdraw_time = None
        announcement.publisher = request.user
        announcement.save()
        messages.success(request, "公告发布成功！")
        return redirect(reverse('announcement_list'))


class AnnouncementWithdrawView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.status = 'withdrawn'
        announcement.withdraw_time = timezone.now()
        announcement.save()
        messages.warning(request, "公告已撤回！")
        return redirect(reverse('announcement_list'))


class OwnerAnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'management/owner_announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        today = timezone.localdate()
        qs = Announcement.objects.filter(
            status='published',
            effective_start_date__lte=today,
            effective_end_date__gte=today
        ).order_by('-is_pinned', '-publish_time')

        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        context['pinned_announcements'] = Announcement.objects.filter(
            status='published',
            is_pinned=True,
            effective_start_date__lte=today,
            effective_end_date__gte=today
        ).order_by('-publish_time')
        context['search_query'] = self.request.GET.get('search', '')
        return context

# --- 车位管理 ---
class ParkingSpotListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ParkingSpot
    template_name = 'management/parking_spot_list.html'
    context_object_name = 'parking_spots'
    paginate_by = 20

    def get_queryset(self):
        qs = ParkingSpot.objects.all()

        estate_id = self.request.GET.get('estate')
        spot_type = self.request.GET.get('spot_type')
        bind_status = self.request.GET.get('bind_status')

        if estate_id:
            qs = qs.filter(estate_id=estate_id)
        if spot_type:
            qs = qs.filter(spot_type=spot_type)
        if bind_status == 'bound':
            qs = qs.filter(owner__isnull=False)
        elif bind_status == 'unbound':
            qs = qs.filter(owner__isnull=True)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estates'] = Estate.objects.all()
        context['spot_types'] = ParkingSpot.TYPE_CHOICES
        context['owners'] = User.objects.filter(role='owner')
        context['units'] = Unit.objects.select_related('floor', 'floor__building', 'floor__building__estate').all()
        context['current_filters'] = {
            'estate': self.request.GET.get('estate', ''),
            'spot_type': self.request.GET.get('spot_type', ''),
            'bind_status': self.request.GET.get('bind_status', ''),
        }
        context['bound_count'] = ParkingSpot.objects.filter(owner__isnull=False).count()
        context['unbound_count'] = ParkingSpot.objects.filter(owner__isnull=True).count()
        total = ParkingSpot.objects.count()
        context['total_count'] = total
        context['bind_rate'] = f"{int(context['bound_count'] / total * 100)}%" if total > 0 else '0%'
        return context

class ParkingSpotCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ParkingSpot
    form_class = ParkingSpotForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('parking_spot_list')

    def form_valid(self, form):
        messages.success(self.request, "车位添加成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增车位"
        return context

class ParkingSpotUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ParkingSpot
    form_class = ParkingSpotForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('parking_spot_list')

    def form_valid(self, form):
        messages.success(self.request, "车位信息更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑车位"
        return context

class ParkingSpotDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ParkingSpot
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('parking_spot_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "车位已删除！")
        return super().delete(request, *args, **kwargs)

class ParkingSpotBindView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        parking_spot = get_object_or_404(ParkingSpot, pk=pk)
        owner_id = request.POST.get('owner_id')
        unit_id = request.POST.get('unit_id')

        if owner_id:
            owner = get_object_or_404(User, pk=owner_id, role='owner')
            parking_spot.owner = owner
        if unit_id:
            unit = get_object_or_404(Unit, pk=unit_id)
            parking_spot.unit = unit

        parking_spot.save()
        messages.success(request, "车位绑定成功！")
        return redirect(reverse('parking_spot_list'))

class ParkingSpotUnbindView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        parking_spot = get_object_or_404(ParkingSpot, pk=pk)
        parking_spot.owner = None
        parking_spot.unit = None
        parking_spot.save()
        messages.success(request, "车位解绑成功！")
        return redirect(reverse('parking_spot_list'))


class ComplaintListView(LoginRequiredMixin, ListView):
    model = ComplaintSuggestion
    template_name = 'management/complaint_list.html'
    context_object_name = 'complaints'
    paginate_by = 20

    def get_queryset(self):
        qs = ComplaintSuggestion.objects.select_related('owner')
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)

        cs_type = self.request.GET.get('cs_type')
        status = self.request.GET.get('status')
        if cs_type:
            qs = qs.filter(cs_type=cs_type)
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cs_types'] = ComplaintSuggestion.TYPE_CHOICES
        context['statuses'] = ComplaintSuggestion.STATUS_CHOICES
        context['current_filters'] = {
            'cs_type': self.request.GET.get('cs_type', ''),
            'status': self.request.GET.get('status', ''),
        }
        return context


class ComplaintCreateView(LoginRequiredMixin, CreateView):
    model = ComplaintSuggestion
    form_class = ComplaintSuggestionForm
    template_name = 'management/complaint_form.html'
    success_url = reverse_lazy('complaint_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "提交成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "提交投诉建议"
        return context


class ComplaintDetailView(LoginRequiredMixin, DetailView):
    model = ComplaintSuggestion
    template_name = 'management/complaint_detail.html'
    context_object_name = 'complaint'

    def get_queryset(self):
        qs = ComplaintSuggestion.objects.select_related('owner').prefetch_related('replies__replier')
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reply_form'] = ComplaintReplyForm()
        context['can_reply'] = self.request.user.role in ['admin', 'staff']
        context['can_close'] = self.request.user.role in ['admin', 'staff']
        return context


class ComplaintReplyView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(ComplaintSuggestion, pk=pk)
        form = ComplaintReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.complaint = complaint
            reply.replier = request.user
            reply.save()
            if complaint.status == 'pending':
                complaint.status = 'replied'
                complaint.save()
            messages.success(request, "回复成功！")
        return redirect(reverse('complaint_detail', kwargs={'pk': complaint.pk}))


class ComplaintCloseView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        complaint = get_object_or_404(ComplaintSuggestion, pk=pk)
        complaint.status = 'closed'
        complaint.save()
        messages.success(request, "工单已关闭！")
        return redirect(reverse('complaint_detail', kwargs={'pk': complaint.pk}))


# --- 快递代收管理 ---
class PackageListView(LoginRequiredMixin, ListView):
    model = Package
    template_name = 'management/package_list.html'
    context_object_name = 'packages'
    paginate_by = 20

    def get_queryset(self):
        qs = Package.objects.select_related('owner', 'unit', 'register_staff', 'handler')
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)

        status = self.request.GET.get('status')
        owner_id = self.request.GET.get('owner')
        arrival_date = self.request.GET.get('arrival_date')

        if status:
            qs = qs.filter(status=status)
        if owner_id and self.request.user.role in ['admin', 'staff']:
            qs = qs.filter(owner_id=owner_id)
        if arrival_date:
            qs = qs.filter(arrival_time__date=arrival_date)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Package.STATUS_CHOICES
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'owner': self.request.GET.get('owner', ''),
            'arrival_date': self.request.GET.get('arrival_date', ''),
        }
        if self.request.user.role in ['admin', 'staff']:
            context['owners'] = User.objects.filter(role='owner')
            context['pending_count'] = Package.objects.filter(status='pending').count()
            context['picked_up_count'] = Package.objects.filter(status='picked_up').count()
            seven_days_ago = timezone.now() - timezone.timedelta(days=7)
            context['overdue_count'] = Package.objects.filter(status='pending', arrival_time__lte=seven_days_ago).count()
        return context


class PackageCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Package
    form_class = PackageForm
    template_name = 'management/package_form.html'
    success_url = reverse_lazy('package_list')

    def form_valid(self, form):
        form.instance.register_staff = self.request.user
        messages.success(self.request, "快递登记成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "快递登记"
        context['is_editing'] = False
        return context


class PackageDetailView(LoginRequiredMixin, DetailView):
    model = Package
    template_name = 'management/package_detail.html'
    context_object_name = 'package'

    def get_queryset(self):
        qs = Package.objects.select_related('owner', 'unit', 'register_staff', 'handler')
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)
        return qs


class PackagePickupView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Package
    form_class = PackagePickupForm
    template_name = 'management/package_form.html'
    success_url = reverse_lazy('package_list')

    def form_valid(self, form):
        form.instance.status = 'picked_up'
        form.instance.handler = self.request.user
        messages.success(self.request, "快递已标记为已领取！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "标记取件"
        context['is_editing'] = True
        context['is_pickup'] = True
        return context


class PackageDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Package
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('package_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "快递记录已删除！")
        return super().delete(request, *args, **kwargs)
