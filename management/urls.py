from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # 楼盘
    path('estate/', views.EstateListView.as_view(), name='estate_list'),
    path('estate/add/', views.EstateCreateView.as_view(), name='estate_add'),
    path('estate/<int:pk>/edit/', views.EstateUpdateView.as_view(), name='estate_edit'),
    path('estate/<int:pk>/delete/', views.EstateDeleteView.as_view(), name='estate_delete'),
    
    # 楼栋
    path('building/', views.BuildingListView.as_view(), name='building_list'),
    path('building/add/', views.BuildingCreateView.as_view(), name='building_add'),
    path('building/<int:pk>/edit/', views.BuildingUpdateView.as_view(), name='building_edit'),
    path('building/<int:pk>/delete/', views.BuildingDeleteView.as_view(), name='building_delete'),
    
    # 楼层
    path('floor/', views.FloorListView.as_view(), name='floor_list'),
    path('floor/add/', views.FloorCreateView.as_view(), name='floor_add'),
    path('floor/<int:pk>/edit/', views.FloorUpdateView.as_view(), name='floor_edit'),
    path('floor/<int:pk>/delete/', views.FloorDeleteView.as_view(), name='floor_delete'),
    
    # 单元(房屋)
    path('unit/', views.UnitListView.as_view(), name='unit_list'),
    path('unit/add/', views.UnitCreateView.as_view(), name='unit_add'),
    path('unit/<int:pk>/edit/', views.UnitUpdateView.as_view(), name='unit_edit'),
    path('unit/<int:pk>/delete/', views.UnitDeleteView.as_view(), name='unit_delete'),
    
    # 业主管理
    path('owner/', views.OwnerListView.as_view(), name='owner_list'),
    path('owner/add/', views.OwnerCreateView.as_view(), name='owner_add'),
    path('owner/<int:pk>/edit/', views.OwnerUpdateView.as_view(), name='owner_edit'),
    path('owner/<int:pk>/delete/', views.OwnerDeleteView.as_view(), name='owner_delete'),
    
    # 报修
    path('repair/', views.RepairListView.as_view(), name='repair_list'),
    path('repair/add/', views.RepairCreateView.as_view(), name='repair_add'),
    path('repair/<int:pk>/process/', views.RepairUpdateView.as_view(), name='repair_process'),
    
    # 费用
    path('fee/', views.FeeListView.as_view(), name='fee_list'),
    path('fee/add/', views.FeeCreateView.as_view(), name='fee_add'),
    path('fee/<int:pk>/process/', views.FeeUpdateView.as_view(), name='fee_process'),
    path('fee/<int:pk>/delete/', views.FeeDeleteView.as_view(), name='fee_delete'),
    
    # 访客管理
    path('visitor/', views.VisitorListView.as_view(), name='visitor_list'),
    path('visitor/add/', views.VisitorCreateView.as_view(), name='visitor_add'),
    path('visitor/<int:pk>/', views.VisitorDetailView.as_view(), name='visitor_detail'),
    path('visitor/<int:pk>/leave/', views.VisitorLeaveView.as_view(), name='visitor_leave'),

    # 社区公告 - 管理端 (admin/staff)
    path('announcement/', views.AnnouncementListView.as_view(), name='announcement_list'),
    path('announcement/add/', views.AnnouncementCreateView.as_view(), name='announcement_add'),
    path('announcement/<int:pk>/edit/', views.AnnouncementUpdateView.as_view(), name='announcement_edit'),
    path('announcement/<int:pk>/delete/', views.AnnouncementDeleteView.as_view(), name='announcement_delete'),
    path('announcement/<int:pk>/detail/', views.AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('announcement/<int:pk>/publish/', views.AnnouncementPublishView.as_view(), name='announcement_publish'),
    path('announcement/<int:pk>/withdraw/', views.AnnouncementWithdrawView.as_view(), name='announcement_withdraw'),

    # 社区公告 - 业主端
    path('notice/', views.OwnerAnnouncementListView.as_view(), name='owner_announcement_list'),
    path('notice/<int:pk>/', views.AnnouncementDetailView.as_view(), name='owner_announcement_detail'),

    # 车位管理
    path('parking/', views.ParkingSpotListView.as_view(), name='parking_spot_list'),
    path('parking/add/', views.ParkingSpotCreateView.as_view(), name='parking_spot_add'),
    path('parking/<int:pk>/edit/', views.ParkingSpotUpdateView.as_view(), name='parking_spot_edit'),
    path('parking/<int:pk>/delete/', views.ParkingSpotDeleteView.as_view(), name='parking_spot_delete'),
    path('parking/<int:pk>/bind/', views.ParkingSpotBindView.as_view(), name='parking_spot_bind'),
    path('parking/<int:pk>/unbind/', views.ParkingSpotUnbindView.as_view(), name='parking_spot_unbind'),

    # 投诉建议
    path('complaint/', views.ComplaintListView.as_view(), name='complaint_list'),
    path('complaint/add/', views.ComplaintCreateView.as_view(), name='complaint_add'),
    path('complaint/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaint/<int:pk>/reply/', views.ComplaintReplyView.as_view(), name='complaint_reply'),
    path('complaint/<int:pk>/close/', views.ComplaintCloseView.as_view(), name='complaint_close'),

    # 快递代收
    path('package/', views.PackageListView.as_view(), name='package_list'),
    path('package/add/', views.PackageCreateView.as_view(), name='package_add'),
    path('package/<int:pk>/', views.PackageDetailView.as_view(), name='package_detail'),
    path('package/<int:pk>/pickup/', views.PackagePickupView.as_view(), name='package_pickup'),
    path('package/<int:pk>/delete/', views.PackageDeleteView.as_view(), name='package_delete'),

    # 社区活动 - 管理端
    path('activity/', views.CommunityActivityListView.as_view(), name='activity_list'),
    path('activity/add/', views.CommunityActivityCreateView.as_view(), name='activity_add'),
    path('activity/<int:pk>/edit/', views.CommunityActivityUpdateView.as_view(), name='activity_edit'),
    path('activity/<int:pk>/delete/', views.CommunityActivityDeleteView.as_view(), name='activity_delete'),
    path('activity/<int:pk>/', views.CommunityActivityDetailView.as_view(), name='activity_detail'),

    # 社区活动 - 业主端
    path('activities/', views.OwnerActivityListView.as_view(), name='owner_activity_list'),
    path('activities/<int:pk>/', views.OwnerActivityDetailView.as_view(), name='owner_activity_detail'),
    path('activities/<int:pk>/register/', views.ActivityRegisterView.as_view(), name='activity_register'),
    path('activities/<int:pk>/cancel/', views.ActivityCancelRegistrationView.as_view(), name='activity_cancel'),

    # 设备设施台账
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/add/', views.EquipmentCreateView.as_view(), name='equipment_add'),
    path('equipment/<int:pk>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_edit'),
    path('equipment/<int:pk>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
    path('equipment/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('equipment/<int:equipment_pk>/log/add/', views.MaintenanceLogAddView.as_view(), name='maintenance_log_add'),

    path('schedule/', views.DutyScheduleListView.as_view(), name='duty_schedule_list'),
    path('schedule/add/', views.DutyScheduleCreateView.as_view(), name='duty_schedule_add'),
    path('schedule/<int:pk>/delete/', views.DutyScheduleDeleteView.as_view(), name='duty_schedule_delete'),
    path('schedule/batch-copy/', views.DutyScheduleBatchCopyView.as_view(), name='duty_schedule_batch_copy'),
    path('schedule/conflict-check/', views.DutyScheduleConflictCheckView.as_view(), name='duty_schedule_conflict_check'),
]
