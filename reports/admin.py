from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Report, AdminNotice, DynamicField, DynamicFieldResponse


# ------------------------------
# ✅ Custom User Admin
# ------------------------------
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Team Info', {'fields': ('team', 'contact')}),
    )
    list_display = ('username', 'email', 'team', 'is_staff')
    list_filter = ('team', 'is_staff')
    search_fields = ('username', 'email')


# ------------------------------
# ✅ Report Admin
# ------------------------------
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_team', 'custom_date', 'created_at')
    list_filter = ('custom_date', 'user__team')
    search_fields = ('user__username', 'tasks')
    ordering = ('-custom_date',)

    def get_team(self, obj):
        return obj.user.team
    get_team.short_description = 'Team'


# ------------------------------
# ✅ AdminNotice Admin
# ------------------------------
@admin.register(AdminNotice)
class AdminNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)


# ------------------------------
# ✅ DynamicField Admin
# ------------------------------
@admin.register(DynamicField)
class DynamicFieldAdmin(admin.ModelAdmin):
    list_display = ('team', 'label', 'field_type', 'required')
    list_filter = ('team', 'field_type')
    search_fields = ('label', 'name')


# ------------------------------
# ✅ DynamicFieldResponse Admin
# ------------------------------
@admin.register(DynamicFieldResponse)
class DynamicFieldResponseAdmin(admin.ModelAdmin):
    list_display = ('report', 'field', 'value')
    list_filter = ('field__team',)
    search_fields = ('report__user__username', 'field__label', 'value')


# ------------------------------
# ✅ Register User
# ------------------------------
admin.site.register(User, CustomUserAdmin)
