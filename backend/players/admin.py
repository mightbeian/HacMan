from django.contrib import admin
from .models import PlayerProfile, PlayerStatistics

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rank', 'total_points', 'challenges_solved', 'created_at']
    list_filter = ['rank', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'avatar')
        }),
        ('Progress', {
            'fields': ('total_points', 'challenges_solved', 'rank', 'badges')
        }),
        ('Category Stats', {
            'fields': ('web_solved', 'crypto_solved', 'stego_solved', 'forensics_solved', 'binary_solved')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PlayerStatistics)
class PlayerStatisticsAdmin(admin.ModelAdmin):
    list_display = ['player', 'total_attempts', 'successful_attempts', 'avg_solve_time', 'last_updated']
    search_fields = ['player__username']
    readonly_fields = ['id', 'last_updated']