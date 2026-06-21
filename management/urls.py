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
]
