from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement, ParkingSpot, ComplaintSuggestion, ComplaintReply, Package, CommunityActivity, ActivityRegistration, Equipment, MaintenanceLog, DutySchedule, DecorationApplication, DecorationReview, MeterReading
from .forms import EstateForm, BuildingForm, FloorForm, UnitForm, OwnerForm, RepairOwnerForm, RepairStaffForm, FeeForm, VisitorForm, VisitorLeaveForm, AnnouncementForm, ParkingSpotForm, ComplaintSuggestionForm, ComplaintReplyForm, PackageForm, PackagePickupForm, CommunityActivityForm, EquipmentForm, MaintenanceLogForm, DutyScheduleForm, DutyScheduleBatchCopyForm, DecorationOwnerForm, DecorationReviewForm, DecorationReviewCommentForm, MeterReadingForm, MeterReadingBatchForm
from django.views.generic import DetailView
from django.utils import timezone
from datetime import date, timedelta
import csv
from django.http import HttpResponse, JsonResponse
from django.db import transaction

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
            context['active_activities'] = CommunityActivity.objects.filter(end_time__gte=timezone.now()).count()
            today = timezone.localdate()
            thirty_days_later = today + timezone.timedelta(days=30)
            context['upcoming_maintenance'] = Equipment.objects.filter(
                next_maintenance_date__lte=thirty_days_later,
                next_maintenance_date__gte=today
            ).count()
            context['overdue_maintenance'] = Equipment.objects.filter(
                next_maintenance_date__lt=today
            ).count()
            context['total_equipment'] = Equipment.objects.count()

            three_days_later = today + timezone.timedelta(days=3)
            context['pending_decorations'] = DecorationApplication.objects.filter(status='pending').count()
            context['in_progress_decorations'] = DecorationApplication.objects.filter(
                status='approved',
                start_date__lte=today,
                end_date__gte=today
            ).count()
            context['ending_soon_decorations'] = DecorationApplication.objects.filter(
                status='approved',
                start_date__lte=today,
                end_date__gte=today,
                end_date__lte=three_days_later
            ).count()
            context['ending_soon_decoration_list'] = DecorationApplication.objects.filter(
                status='approved',
                start_date__lte=today,
                end_date__gte=today,
                end_date__lte=three_days_later
            ).select_related('owner', 'unit', 'unit__floor', 'unit__floor__building').order_by('end_date')[:5]

            if self.request.user.role == 'staff':
                today_date = timezone.localdate()
                start_of_week = today_date - timedelta(days=today_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                context['my_weekly_duties'] = DutySchedule.objects.filter(
                    staff=self.request.user,
                    date__gte=start_of_week,
                    date__lte=end_of_week
                ).order_by('date', 'shift')
                context['week_start'] = start_of_week
                context['week_end'] = end_of_week
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
            now = timezone.now()
            context['my_registered_activities'] = CommunityActivity.objects.filter(
                end_time__gte=now,
                registrations__owner=self.request.user
            ).order_by('start_time')[:5]
            context['available_activities'] = CommunityActivity.objects.filter(
                end_time__gte=now,
                registration_deadline__gte=now
            ).order_by('start_time')[:5]
            context['my_decorations'] = DecorationApplication.objects.filter(
                owner=self.request.user
            ).order_by('-created_at')[:5]

            my_unit_ids = list(Unit.objects.filter(owner=self.request.user).values_list('id', flat=True))
            if my_unit_ids:
                water_readings = MeterReading.objects.filter(
                    unit_id__in=my_unit_ids,
                    meter_type='water'
                ).select_related('unit').order_by('-reading_month')[:3 * len(my_unit_ids)]
                electric_readings = MeterReading.objects.filter(
                    unit_id__in=my_unit_ids,
                    meter_type='electric'
                ).select_related('unit').order_by('-reading_month')[:3 * len(my_unit_ids)]

                water_by_unit = {}
                electric_by_unit = {}
                for r in water_readings:
                    water_by_unit.setdefault(r.unit_id, []).append(r)
                for r in electric_readings:
                    electric_by_unit.setdefault(r.unit_id, []).append(r)

                meter_summary = []
                for unit in context['my_units']:
                    water_list = list(reversed(water_by_unit.get(unit.id, [])))
                    electric_list = list(reversed(electric_by_unit.get(unit.id, [])))

                    def calc_recent_with_change(readings_list):
                        if not readings_list:
                            return [], None
                        recent = readings_list[-3:]
                        last = recent[-1]
                        change_rate = last.usage_change_rate
                        return recent, change_rate

                    water_recent, water_change = calc_recent_with_change(water_list)
                    electric_recent, electric_change = calc_recent_with_change(electric_list)

                    meter_summary.append({
                        'unit': unit,
                        'water_recent': water_recent,
                        'water_change': water_change,
                        'electric_recent': electric_recent,
                        'electric_change': electric_change,
                    })
                context['meter_summary'] = meter_summary
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

@login_required
def get_owner_units(request, owner_id):
    if request.user.role not in ['admin', 'staff']:
        return JsonResponse({'error': '无权限访问'}, status=403)
    try:
        owner = User.objects.get(pk=owner_id, role='owner')
        units = Unit.objects.filter(owner=owner)
        unit_list = [{'id': u.id, 'name': str(u)} for u in units]
        return JsonResponse({'units': unit_list})
    except User.DoesNotExist:
        return JsonResponse({'units': []})

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
        today = timezone.localdate()
        import re

        def _strip_html(html_content):
            if not html_content:
                return ''
            clean = re.compile('<.*?>')
            text = re.sub(clean, '', html_content)
            text = text.replace('&nbsp;', ' ').replace('&zwj;', '').replace('\u200b', '')
            return text.strip()

        plain_text = _strip_html(announcement.content)
        if not plain_text or len(plain_text) < 3:
            messages.error(request, "发布失败：公告正文内容为空或过短，请先编辑正文内容。")
            return redirect(reverse('announcement_edit', args=[pk]))

        if announcement.effective_end_date < today:
            messages.error(
                request,
                f"发布失败：生效结束日期（{announcement.effective_end_date.strftime('%Y-%m-%d')}）"
                f"已早于今天（{today.strftime('%Y-%m-%d')}），业主端将无法看到此公告。"
                f"请先编辑并调整生效日期后再发布。"
            )
            return redirect(reverse('announcement_edit', args=[pk]))

        if not announcement.title or len(announcement.title.strip()) < 2:
            messages.error(request, "发布失败：公告标题不能为空或过短。")
            return redirect(reverse('announcement_edit', args=[pk]))

        announcement.status = 'published'
        announcement.publish_time = timezone.now()
        announcement.withdraw_time = None
        announcement.publisher = request.user
        announcement.save()
        messages.success(request, "公告发布成功！业主端已可见。")
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
        all_units = Unit.objects.select_related('floor', 'floor__building', 'floor__building__estate').all()
        context['units'] = all_units
        
        owner_units = {}
        for unit in all_units:
            if unit.owner_id:
                if unit.owner_id not in owner_units:
                    owner_units[unit.owner_id] = []
                owner_units[unit.owner_id].append({
                    'id': unit.id,
                    'name': f"{unit.floor.building.name} - {unit.name}",
                    'full_name': f"{unit.floor.building.estate.name} - {unit.floor.building.name} - {unit.name}"
                })
        import json
        context['owner_units_json'] = json.dumps(owner_units, ensure_ascii=False)
        
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
        if not form.instance.owner:
            form.instance.unit = None
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
        if not form.instance.owner:
            form.instance.unit = None
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

        if not owner_id:
            messages.error(request, "绑定失败：请选择要绑定的业主！")
            return redirect(reverse('parking_spot_list'))

        owner = get_object_or_404(User, pk=owner_id, role='owner')
        parking_spot.owner = owner

        if unit_id:
            unit = get_object_or_404(Unit, pk=unit_id)
            if unit.owner and unit.owner_id != int(owner_id):
                messages.error(request, f"绑定失败：单元 {unit.floor.building.name}-{unit.name} 不属于业主 {owner.username}！")
                return redirect(reverse('parking_spot_list'))
            parking_spot.unit = unit
        else:
            parking_spot.unit = None

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


# --- 社区活动管理 ---
class CommunityActivityListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = CommunityActivity
    template_name = 'management/activity_list.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        tab = self.request.GET.get('tab', 'active')
        now = timezone.now()
        qs = CommunityActivity.objects.prefetch_related('registrations__owner')

        search = self.request.GET.get('search')

        if tab == 'active':
            qs = qs.filter(end_time__gte=now)
        elif tab == 'history':
            qs = qs.filter(end_time__lt=now)

        if search:
            qs = qs.filter(title__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_tab'] = self.request.GET.get('tab', 'active')
        context['current_filters'] = {
            'search': self.request.GET.get('search', ''),
        }
        context['now'] = timezone.now()
        return context

    def get(self, request, *args, **kwargs):
        if 'export' in request.GET and request.user.role in ['admin', 'staff']:
            activity_id = request.GET.get('activity_id')
            if activity_id:
                activity = get_object_or_404(CommunityActivity, pk=activity_id)
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="activity_{activity_id}_registrations.csv"'
                response.write('\xEF\xBB\xBF')

                writer = csv.writer(response)
                writer.writerow(['序号', '业主姓名', '联系电话', '报名时间'])

                for idx, reg in enumerate(activity.registrations.select_related('owner').all(), 1):
                    writer.writerow([
                        idx,
                        reg.owner.get_full_name() or reg.owner.username,
                        reg.owner.phone or '-',
                        reg.registered_at.strftime('%Y-%m-%d %H:%M'),
                    ])
                return response
        return super().get(request, *args, **kwargs)


class CommunityActivityCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = CommunityActivity
    form_class = CommunityActivityForm
    template_name = 'management/activity_form.html'
    success_url = reverse_lazy('activity_list')

    def form_valid(self, form):
        form.instance.publisher = self.request.user
        messages.success(self.request, "社区活动发布成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "发布社区活动"
        context['is_editing'] = False
        return context


class CommunityActivityUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = CommunityActivity
    form_class = CommunityActivityForm
    template_name = 'management/activity_form.html'
    success_url = reverse_lazy('activity_list')

    def form_valid(self, form):
        messages.success(self.request, "活动信息更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑社区活动"
        context['is_editing'] = True
        return context


class CommunityActivityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = CommunityActivity
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('activity_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "活动已删除！")
        return super().delete(request, *args, **kwargs)


class CommunityActivityDetailView(LoginRequiredMixin, DetailView):
    model = CommunityActivity
    template_name = 'management/activity_detail.html'
    context_object_name = 'activity'

    def get_queryset(self):
        qs = CommunityActivity.objects.prefetch_related('registrations__owner')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        if self.request.user.role == 'owner':
            context['has_registered'] = ActivityRegistration.objects.filter(
                activity=self.object,
                owner=self.request.user
            ).exists()
        return context


class ActivityRegisterView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(CommunityActivity, pk=pk)
        now = timezone.now()

        if now > activity.registration_deadline:
            messages.error(request, "报名已截止！")
            return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))

        if activity.is_full:
            messages.error(request, "活动名额已满！")
            return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))

        if ActivityRegistration.objects.filter(activity=activity, owner=request.user).exists():
            messages.warning(request, "您已报名过此活动！")
            return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))

        ActivityRegistration.objects.create(activity=activity, owner=request.user)
        messages.success(request, "报名成功！")
        return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))


class ActivityCancelRegistrationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(CommunityActivity, pk=pk)
        registration = ActivityRegistration.objects.filter(activity=activity, owner=request.user).first()

        if not registration:
            messages.warning(request, "您尚未报名此活动！")
            return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))

        if not activity.is_registration_open:
            messages.error(request, "报名已截止，无法取消报名！")
            return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))

        registration.delete()
        messages.success(request, "已取消报名！")
        return redirect(reverse('owner_activity_detail', kwargs={'pk': activity.pk}))


class OwnerActivityListView(LoginRequiredMixin, ListView):
    model = CommunityActivity
    template_name = 'management/owner_activity_list.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        now = timezone.now()
        qs = CommunityActivity.objects.filter(end_time__gte=now).prefetch_related('registrations').order_by('start_time')

        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(title__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        now = timezone.now()

        registered_ids = ActivityRegistration.objects.filter(
            owner=self.request.user
        ).values_list('activity_id', flat=True)
        context['registered_ids'] = list(registered_ids)
        context['now'] = now
        return context


class OwnerActivityDetailView(LoginRequiredMixin, DetailView):
    model = CommunityActivity
    template_name = 'management/owner_activity_detail.html'
    context_object_name = 'activity'

    def get_queryset(self):
        return CommunityActivity.objects.prefetch_related('registrations__owner')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['has_registered'] = ActivityRegistration.objects.filter(
            activity=self.object,
            owner=self.request.user
        ).exists()
        return context


# --- 设备设施台账 ---
class EquipmentListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Equipment
    template_name = 'management/equipment_list.html'
    context_object_name = 'equipments'
    paginate_by = 20

    def get_queryset(self):
        qs = Equipment.objects.select_related('estate', 'responsible_person').prefetch_related('maintenance_logs')

        estate_id = self.request.GET.get('estate')
        maintenance_status = self.request.GET.get('maintenance_status')
        search = self.request.GET.get('search')

        if estate_id:
            qs = qs.filter(estate_id=estate_id)

        today = timezone.localdate()
        thirty_days_later = today + timezone.timedelta(days=30)
        if maintenance_status == 'overdue':
            qs = qs.filter(next_maintenance_date__lt=today)
        elif maintenance_status == 'due_soon':
            qs = qs.filter(next_maintenance_date__lte=thirty_days_later, next_maintenance_date__gte=today)
        elif maintenance_status == 'normal':
            qs = qs.filter(next_maintenance_date__gt=thirty_days_later)

        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(installation_location__icontains=search) | qs.filter(brand_model__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        thirty_days_later = today + timezone.timedelta(days=30)

        context['estates'] = Estate.objects.all()
        context['current_filters'] = {
            'estate': self.request.GET.get('estate', ''),
            'maintenance_status': self.request.GET.get('maintenance_status', ''),
            'search': self.request.GET.get('search', ''),
        }
        context['total_count'] = Equipment.objects.count()
        context['overdue_count'] = Equipment.objects.filter(next_maintenance_date__lt=today).count()
        context['due_soon_count'] = Equipment.objects.filter(
            next_maintenance_date__lte=thirty_days_later,
            next_maintenance_date__gte=today
        ).count()
        context['normal_count'] = Equipment.objects.filter(next_maintenance_date__gt=thirty_days_later).count()
        context['today'] = today
        return context


class EquipmentCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('equipment_list')

    def form_valid(self, form):
        messages.success(self.request, "设备信息添加成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增设备档案"
        return context


class EquipmentUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('equipment_list')

    def form_valid(self, form):
        messages.success(self.request, "设备信息更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑设备档案"
        return context


class EquipmentDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Equipment
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('equipment_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "设备档案已删除！")
        return super().delete(request, *args, **kwargs)


class EquipmentDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Equipment
    template_name = 'management/equipment_detail.html'
    context_object_name = 'equipment'

    def get_queryset(self):
        return Equipment.objects.select_related('estate', 'responsible_person').prefetch_related('maintenance_logs__operator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['maintenance_log_form'] = MaintenanceLogForm()
        context['today'] = timezone.localdate()
        return context


class MaintenanceLogAddView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, equipment_pk):
        equipment = get_object_or_404(Equipment, pk=equipment_pk)
        form = MaintenanceLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.equipment = equipment
            log.save()
            messages.success(request, "维保日志已记录！")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect(reverse('equipment_detail', kwargs={'pk': equipment_pk}))


class DutyScheduleListView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'management/schedule_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import calendar
        year = int(self.request.GET.get('year', timezone.localdate().year))
        month = int(self.request.GET.get('month', timezone.localdate().month))
        cal = calendar.monthcalendar(year, month)
        first_day = date(year, month, 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        schedules = DutySchedule.objects.filter(
            date__gte=first_day,
            date__lte=last_day
        ).select_related('staff').order_by('shift')
        schedule_map = {}
        for s in schedules:
            key = s.date.day
            if key not in schedule_map:
                schedule_map[key] = []
            schedule_map[key].append(s)
        context['year'] = year
        context['month'] = month
        context['cal'] = cal
        context['schedule_map'] = schedule_map
        context['staff_list'] = User.objects.filter(role__in=['admin', 'staff'])
        if month == 12:
            context['prev_year'], context['prev_month'] = year, 11
            context['next_year'], context['next_month'] = year + 1, 1
        elif month == 1:
            context['prev_year'], context['prev_month'] = year - 1, 12
            context['next_year'], context['next_month'] = year, 2
        else:
            context['prev_year'], context['prev_month'] = year, month - 1
            context['next_year'], context['next_month'] = year, month + 1
        context['today'] = timezone.localdate()
        context['batch_copy_form'] = DutyScheduleBatchCopyForm()
        last_week_start = timezone.localdate() - timedelta(days=timezone.localdate().weekday() + 7)
        context['last_week_start'] = last_week_start
        return context


class DutyScheduleCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = DutySchedule
    form_class = DutyScheduleForm
    template_name = 'management/schedule_form.html'
    success_url = reverse_lazy('duty_schedule_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "排班添加成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "新增排班"
        initial_date = self.request.GET.get('date')
        if initial_date and not self.request.POST:
            context['form'].initial['date'] = initial_date
        return context


class DutyScheduleDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = DutySchedule
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('duty_schedule_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "排班记录已删除！")
        return super().delete(request, *args, **kwargs)


class DutyScheduleBatchCopyView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request):
        form = DutyScheduleBatchCopyForm(request.POST)
        if form.is_valid():
            source_start = form.cleaned_data['source_week_start']
            target_start = form.cleaned_data['target_week_start']
            delta = target_start - source_start
            source_schedules = DutySchedule.objects.filter(
                date__gte=source_start,
                date__lt=source_start + timedelta(days=7)
            )
            if not source_schedules.exists():
                messages.warning(request, "源周没有任何排班数据，无法复制！")
                return redirect(reverse('duty_schedule_list'))
            copied = 0
            skipped = 0
            conflicts = []
            for s in source_schedules:
                new_date = s.date + delta
                if DutySchedule.objects.filter(date=new_date, shift=s.shift, staff=s.staff).exists():
                    skipped += 1
                    conflicts.append(f"{s.staff.username} 在 {new_date} 的{dict(DutySchedule.SHIFT_CHOICES).get(s.shift, s.shift)}")
                    continue
                DutySchedule.objects.create(
                    date=new_date,
                    shift=s.shift,
                    staff=s.staff,
                    remarks=s.remarks,
                    created_by=request.user
                )
                copied += 1
            msg = f"批量复制完成！成功复制 {copied} 条"
            if skipped > 0:
                msg += f"，跳过 {skipped} 条冲突（{'；'.join(conflicts)}）"
            messages.success(request, msg)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect(reverse('duty_schedule_list'))


class DutyScheduleConflictCheckView(LoginRequiredMixin, StaffRequiredMixin, View):
    def get(self, request):
        date_val = request.GET.get('date')
        shift_val = request.GET.get('shift')
        staff_val = request.GET.get('staff')
        schedule_id = request.GET.get('schedule_id')
        if not all([date_val, shift_val, staff_val]):
            return JsonResponse({'conflict': False})
        qs = DutySchedule.objects.filter(date=date_val, shift=shift_val, staff_id=staff_val)
        if schedule_id:
            qs = qs.exclude(pk=schedule_id)
        if qs.exists():
            existing = qs.first()
            return JsonResponse({
                'conflict': True,
                'message': f"冲突：{existing.staff.username} 在 {date_val} 的{dict(DutySchedule.SHIFT_CHOICES).get(shift_val, shift_val)}已有排班记录！"
            })
        return JsonResponse({'conflict': False})


class DecorationListView(LoginRequiredMixin, ListView):
    model = DecorationApplication
    template_name = 'management/decoration_list.html'
    context_object_name = 'decorations'
    paginate_by = 20

    def get_queryset(self):
        qs = DecorationApplication.objects.select_related('owner', 'unit', 'unit__floor', 'unit__floor__building', 'unit__floor__building__estate').prefetch_related('reviews')
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)

        status = self.request.GET.get('status')
        decoration_type = self.request.GET.get('decoration_type')
        if status:
            qs = qs.filter(status=status)
        if decoration_type:
            qs = qs.filter(decoration_type=decoration_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = DecorationApplication.STATUS_CHOICES
        context['decoration_types'] = DecorationApplication.DECORATION_TYPE_CHOICES
        context['current_filters'] = {
            'status': self.request.GET.get('status', ''),
            'decoration_type': self.request.GET.get('decoration_type', ''),
        }
        if self.request.user.role in ['admin', 'staff']:
            context['pending_count'] = DecorationApplication.objects.filter(status='pending').count()
            context['in_progress_count'] = DecorationApplication.objects.filter(status='approved').count()
        return context


class DecorationCreateView(LoginRequiredMixin, CreateView):
    model = DecorationApplication
    form_class = DecorationOwnerForm
    template_name = 'management/decoration_form.html'
    success_url = reverse_lazy('decoration_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.role == 'owner':
            kwargs['owner'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "装修申请提交成功！请等待物业审核。")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "提交装修申请"
        context['is_editing'] = False
        return context


class DecorationDetailView(LoginRequiredMixin, DetailView):
    model = DecorationApplication
    template_name = 'management/decoration_detail.html'
    context_object_name = 'decoration'

    def get_queryset(self):
        qs = DecorationApplication.objects.select_related('owner', 'unit', 'unit__floor', 'unit__floor__building', 'unit__floor__building__estate', 'reviewer').prefetch_related('reviews__replier')
        if self.request.user.role == 'owner':
            qs = qs.filter(owner=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.localdate()
        if self.request.user.role in ['admin', 'staff'] and self.object.status == 'pending':
            context['review_form'] = DecorationReviewForm()
        context['comment_form'] = DecorationReviewCommentForm()
        return context


class DecorationReviewView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(DecorationApplication, pk=pk, status='pending')
        form = DecorationReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            opinion = form.cleaned_data['opinion']

            application.status = action
            application.reviewer = request.user
            application.review_opinion = opinion
            application.review_time = timezone.now()
            application.save()

            DecorationReview.objects.create(
                application=application,
                reviewer=request.user,
                action=action,
                opinion=opinion
            )

            action_text = dict(DecorationReviewForm.REVIEW_ACTION_CHOICES).get(action, action)
            messages.success(request, f"审核操作已完成：{action_text}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect(reverse('decoration_detail', kwargs={'pk': pk}))


class DecorationCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(DecorationApplication, pk=pk)
        if request.user.role == 'owner' and application.owner != request.user:
            messages.error(request, "您没有权限对此申请进行评论")
            return redirect(reverse('decoration_list'))
        if request.user.role not in ['admin', 'staff'] and application.owner != request.user:
            messages.error(request, "您没有权限对此申请进行评论")
            return redirect(reverse('decoration_list'))

        form = DecorationReviewCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.application = application
            comment.reviewer = request.user
            if application.status == 'need_materials' and request.user.role == 'owner':
                comment.action = 'pending'
                application.status = 'pending'
                application.save()
            else:
                comment.action = application.status
            comment.save()
            messages.success(request, "评论已提交")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect(reverse('decoration_detail', kwargs={'pk': pk}))


class DecorationInProgressListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = DecorationApplication
    template_name = 'management/decoration_in_progress.html'
    context_object_name = 'decorations'
    paginate_by = 20

    def get_queryset(self):
        today = timezone.localdate()
        qs = DecorationApplication.objects.select_related('owner', 'unit', 'unit__floor', 'unit__floor__building', 'unit__floor__building__estate').filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).order_by('end_date')

        ending_soon = self.request.GET.get('ending_soon')
        if ending_soon == '1':
            three_days_later = today + timedelta(days=3)
            qs = qs.filter(end_date__lte=three_days_later)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        context['today'] = today
        context['total_count'] = DecorationApplication.objects.filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today
        ).count()
        three_days_later = today + timedelta(days=3)
        context['ending_soon_count'] = DecorationApplication.objects.filter(
            status='approved',
            start_date__lte=today,
            end_date__gte=today,
            end_date__lte=three_days_later
        ).count()
        context['current_filters'] = {
            'ending_soon': self.request.GET.get('ending_soon', ''),
        }
        return context


class DecorationCompleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        application = get_object_or_404(DecorationApplication, pk=pk)
        if application.status != 'approved':
            messages.error(request, "只有审核通过的申请才能标记为完成")
            return redirect(reverse('decoration_detail', kwargs={'pk': pk}))

        application.status = 'completed'
        application.save()

        DecorationReview.objects.create(
            application=application,
            reviewer=request.user,
            action='completed',
            opinion="施工已完成，申请已关闭。"
        )

        messages.success(request, "装修申请已标记为施工完成")
        return redirect(reverse('decoration_in_progress'))


class MeterReadingListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = MeterReading
    template_name = 'management/meter_reading_list.html'
    context_object_name = 'readings'
    paginate_by = 30

    def get_queryset(self):
        qs = MeterReading.objects.select_related(
            'unit', 'unit__floor', 'unit__floor__building',
            'unit__floor__building__estate', 'recorded_by'
        )

        estate_id = self.request.GET.get('estate')
        building_id = self.request.GET.get('building')
        reading_month = self.request.GET.get('reading_month')
        meter_type = self.request.GET.get('meter_type')

        if estate_id:
            qs = qs.filter(unit__floor__building__estate_id=estate_id)
        if building_id:
            qs = qs.filter(unit__floor__building_id=building_id)
        if reading_month:
            try:
                year, month = map(int, reading_month.split('-'))
                qs = qs.filter(reading_month__year=year, reading_month__month=month)
            except (ValueError, AttributeError):
                pass
        if meter_type:
            qs = qs.filter(meter_type=meter_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estates'] = Estate.objects.all()
        context['buildings'] = Building.objects.select_related('estate').all()
        context['meter_types'] = MeterReading.METER_TYPE_CHOICES
        context['current_filters'] = {
            'estate': self.request.GET.get('estate', ''),
            'building': self.request.GET.get('building', ''),
            'reading_month': self.request.GET.get('reading_month', ''),
            'meter_type': self.request.GET.get('meter_type', ''),
        }
        context['batch_form'] = MeterReadingBatchForm()
        context['total_readings'] = MeterReading.objects.count()
        context['first_reading_count'] = MeterReading.objects.filter(is_first_reading=True).count()
        return context


class MeterReadingCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('meter_reading_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        reading_month = form.cleaned_data.get('reading_month')
        if reading_month:
            form.instance.reading_month = reading_month.replace(day=1)
        messages.success(self.request, "抄表记录录入成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "录入抄表记录"
        return context


class MeterReadingDetailView(LoginRequiredMixin, DetailView):
    model = MeterReading
    template_name = 'management/meter_reading_detail.html'
    context_object_name = 'reading'

    def get_queryset(self):
        qs = MeterReading.objects.select_related(
            'unit', 'unit__floor', 'unit__floor__building',
            'unit__floor__building__estate', 'unit__owner', 'recorded_by'
        )
        if self.request.user.role == 'owner':
            qs = qs.filter(unit__owner=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous = MeterReading.objects.filter(
            unit=self.object.unit,
            meter_type=self.object.meter_type,
            reading_month__lt=self.object.reading_month
        ).order_by('-reading_month').first()
        context['previous_reading_obj'] = previous
        context['change_rate'] = self.object.usage_change_rate
        return context


class MeterReadingUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = MeterReading
    form_class = MeterReadingForm
    template_name = 'management/form.html'
    success_url = reverse_lazy('meter_reading_list')

    def form_valid(self, form):
        form.instance.recorded_by = self.request.user
        reading_month = form.cleaned_data.get('reading_month')
        if reading_month:
            form.instance.reading_month = reading_month.replace(day=1)
        if self.object.current_reading >= self.object.previous_reading:
            form.instance.usage = form.instance.current_reading - form.instance.previous_reading
        else:
            form.instance.usage = 0
        messages.success(self.request, "抄表记录更新成功！")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "编辑抄表记录"
        return context


class MeterReadingDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = MeterReading
    template_name = 'management/confirm_delete.html'
    success_url = reverse_lazy('meter_reading_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, "抄表记录已删除！")
        return super().delete(request, *args, **kwargs)


class MeterReadingBatchEntryView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = 'management/meter_reading_batch.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        batch_form = MeterReadingBatchForm(self.request.GET or None)
        context['batch_form'] = batch_form
        context['units_data'] = []

        if batch_form.is_valid():
            reading_month = batch_form.cleaned_data['reading_month']
            meter_type = batch_form.cleaned_data['meter_type']
            estate = batch_form.cleaned_data.get('estate')
            building = batch_form.cleaned_data.get('building')

            units_qs = Unit.objects.select_related(
                'floor', 'floor__building', 'floor__building__estate', 'owner'
            )
            if estate:
                units_qs = units_qs.filter(floor__building__estate=estate)
            if building:
                units_qs = units_qs.filter(floor__building=building)

            existing_readings = {
                r.unit_id: r for r in MeterReading.objects.filter(
                    reading_month=reading_month,
                    meter_type=meter_type,
                    unit__in=units_qs.values_list('id', flat=True)
                )
            }

            for unit in units_qs:
                existing = existing_readings.get(unit.id)
                previous = MeterReading.objects.filter(
                    unit=unit,
                    meter_type=meter_type,
                    reading_month__lt=reading_month
                ).order_by('-reading_month').first()
                context['units_data'].append({
                    'unit': unit,
                    'existing': existing,
                    'previous_reading': previous.current_reading if previous else 0,
                    'is_first': previous is None,
                    'current_reading': existing.current_reading if existing else '',
                    'reading_id': existing.id if existing else None,
                })
            context['reading_month'] = reading_month
            context['meter_type'] = meter_type
            context['meter_type_display'] = dict(MeterReading.METER_TYPE_CHOICES).get(meter_type, '')
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        reading_month_str = request.POST.get('reading_month')
        meter_type = request.POST.get('meter_type')

        if not reading_month_str or not meter_type:
            messages.error(request, "请选择抄表月份和抄表类型")
            return redirect(reverse('meter_reading_batch'))

        try:
            year, month = map(int, reading_month_str.split('-'))
            reading_month = date(year, month, 1)
        except (ValueError, AttributeError):
            messages.error(request, "抄表月份格式错误")
            return redirect(reverse('meter_reading_batch'))

        unit_ids = request.POST.getlist('unit_id[]')
        current_readings = request.POST.getlist('current_reading[]')
        remarks_list = request.POST.getlist('remarks[]')

        success_count = 0
        skip_count = 0
        error_count = 0

        for idx, unit_id in enumerate(unit_ids):
            try:
                unit_id = int(unit_id)
                reading_val = current_readings[idx] if idx < len(current_readings) else ''
                remarks = remarks_list[idx] if idx < len(remarks_list) else ''

                if not reading_val:
                    skip_count += 1
                    continue

                try:
                    reading_val = float(reading_val)
                except ValueError:
                    error_count += 1
                    continue

                existing = MeterReading.objects.filter(
                    unit_id=unit_id,
                    meter_type=meter_type,
                    reading_month=reading_month
                ).first()

                if existing:
                    existing.current_reading = reading_val
                    if reading_val >= existing.previous_reading:
                        existing.usage = reading_val - existing.previous_reading
                    else:
                        existing.usage = 0
                    existing.remarks = remarks
                    existing.recorded_by = request.user
                    existing.save()
                    success_count += 1
                else:
                    MeterReading.objects.create(
                        unit_id=unit_id,
                        meter_type=meter_type,
                        reading_month=reading_month,
                        current_reading=reading_val,
                        remarks=remarks,
                        recorded_by=request.user
                    )
                    success_count += 1
            except Exception:
                error_count += 1

        msg = f"批量处理完成！成功 {success_count} 条"
        if skip_count:
            msg += f"，跳过空值 {skip_count} 条"
        if error_count:
            msg += f"，失败 {error_count} 条"
        messages.success(request, msg)
        return redirect(
            reverse('meter_reading_list')
            + f'?reading_month={reading_month_str}&meter_type={meter_type}'
        )
