from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, View
from django.contrib import messages
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement
from .forms import EstateForm, BuildingForm, FloorForm, UnitForm, OwnerForm, RepairOwnerForm, RepairStaffForm, FeeForm, VisitorForm, VisitorLeaveForm, AnnouncementForm
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
        else:
            context['my_units'] = Unit.objects.filter(owner=self.request.user)
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
