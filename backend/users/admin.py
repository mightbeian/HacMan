from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Badge, UserBadge

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'total_points', 'rank', 'challenges_completed']
    list_filter = ['rank', 'created_at']
    search_fields = ['username', 'email']
    ordering = ['-total_points']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('CTF Stats', {'fields': ('total_points', 'rank', 'current_streak', 
                                   'longest_streak', 'challenges_completed')}),
        ('Profile', {'fields': ('avatar_url', 'bio')}),
    )

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'requirement_type', 'requirement_value', 'created_at']
    search_fields = ['name', 'description']

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['earned_at']
    search_fields = ['user__username', 'badge__name']
