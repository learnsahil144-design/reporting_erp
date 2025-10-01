from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Report

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Team Info', {'fields': ('team', 'contact')}),
    )
    list_display = ('username', 'email', 'team', 'is_staff')
    list_filter = ('team', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_team', 'custom_date', 'created_at')
    list_filter = ('custom_date', 'user')
    search_fields = ('user__username', 'tasks')
    ordering = ('-custom_date',)

    def get_team(self, obj):
        return obj.user.team  # 👈 pulling team from User model
    get_team.short_description = 'Team'  # display column header


admin.site.register(User, CustomUserAdmin)
