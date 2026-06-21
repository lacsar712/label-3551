from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Estate, Building, Floor, Unit, Repair, Fee, Visitor

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('角色信息', {'fields': ('role', 'phone')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Estate)
admin.site.register(Building)
admin.site.register(Floor)
admin.site.register(Unit)
admin.site.register(Repair)
admin.site.register(Fee)
admin.site.register(Visitor)
