from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement, ParkingSpot, ComplaintSuggestion, ComplaintReply, Package, CommunityActivity, ActivityRegistration, Equipment, MaintenanceLog

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('角色信息', {'fields': ('role', 'phone')}),
    )

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_pinned', 'effective_start_date', 'effective_end_date', 'publisher', 'publish_time')
    list_filter = ('status', 'is_pinned')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

admin.site.register(User, CustomUserAdmin)
admin.site.register(Estate)
admin.site.register(Building)
admin.site.register(Floor)
admin.site.register(Unit)
admin.site.register(Repair)
admin.site.register(Fee)
admin.site.register(Visitor)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(ParkingSpot)


class ComplaintReplyInline(admin.TabularInline):
    model = ComplaintReply
    extra = 0
    readonly_fields = ('replier', 'content', 'created_at')


class ComplaintSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'cs_type', 'title', 'owner', 'is_anonymous', 'status', 'created_at')
    list_filter = ('cs_type', 'status', 'is_anonymous')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    inlines = [ComplaintReplyInline]


admin.site.register(ComplaintSuggestion, ComplaintSuggestionAdmin)
admin.site.register(ComplaintReply)


class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'courier_company', 'tracking_last4', 'owner', 'package_size', 'storage_location', 'status', 'arrival_time', 'pickup_time')
    list_filter = ('status', 'courier_company', 'package_size')
    search_fields = ('tracking_last4', 'owner__username', 'storage_location')
    date_hierarchy = 'arrival_time'
    readonly_fields = ('arrival_time', 'register_staff', 'pickup_time', 'handler')


admin.site.register(Package, PackageAdmin)


class ActivityRegistrationInline(admin.TabularInline):
    model = ActivityRegistration
    extra = 0
    readonly_fields = ('owner', 'registered_at')


class CommunityActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'start_time', 'end_time', 'max_participants', 'registration_deadline', 'publisher', 'created_at')
    list_filter = ('publisher',)
    search_fields = ('title', 'location', 'description')
    date_hierarchy = 'created_at'
    inlines = [ActivityRegistrationInline]


admin.site.register(CommunityActivity, CommunityActivityAdmin)
admin.site.register(ActivityRegistration)


class MaintenanceLogInline(admin.TabularInline):
    model = MaintenanceLog
    extra = 0
    readonly_fields = ('created_at',)


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'estate', 'installation_location', 'brand_model', 'next_maintenance_date', 'responsible_person', 'maintenance_status')
    list_filter = ('estate', 'responsible_person')
    search_fields = ('name', 'installation_location', 'brand_model')
    date_hierarchy = 'next_maintenance_date'
    inlines = [MaintenanceLogInline]

    def maintenance_status(self, obj):
        from django.utils.html import format_html
        if obj.is_maintenance_overdue:
            return format_html('<span class="badge bg-danger">已过期 {} 天</span>', -obj.days_until_maintenance)
        elif obj.is_maintenance_due_soon:
            return format_html('<span class="badge bg-warning text-dark">{} 天后到期</span>', obj.days_until_maintenance)
        return format_html('<span class="badge bg-success">正常</span>')
    maintenance_status.short_description = '维保状态'


admin.site.register(Equipment, EquipmentAdmin)


class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'maintenance_date', 'operator', 'cost', 'created_at')
    list_filter = ('maintenance_date', 'operator')
    search_fields = ('equipment__name', 'content')
    date_hierarchy = 'maintenance_date'


admin.site.register(MaintenanceLog, MaintenanceLogAdmin)
