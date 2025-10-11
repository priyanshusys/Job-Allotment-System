from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Job, Report
#admins3
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Job)
admin.site.register(Report)
