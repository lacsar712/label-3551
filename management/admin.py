from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor, Announcement, ParkingSpot

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
