from django.contrib import admin
from .models import Challenge, Submission, HintRequest

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'points', 'solve_count', 'is_active', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'author__username']
    readonly_fields = ['id', 'flag_hash', 'solve_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'difficulty', 'author')
        }),
        ('Challenge Details', {
            'fields': ('points', 'flag', 'flag_hash', 'hints', 'files', 'url')
        }),
        ('Status', {
            'fields': ('is_active', 'solve_count')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['player', 'challenge', 'is_correct', 'solve_time_seconds', 'hints_used', 'submitted_at']
    list_filter = ['is_correct', 'submitted_at', 'challenge__category']
    search_fields = ['player__username', 'challenge__title']
    readonly_fields = ['id', 'submitted_at']

@admin.register(HintRequest)
class HintRequestAdmin(admin.ModelAdmin):
    list_display = ['player', 'challenge', 'hint_level', 'requested_at']
    list_filter = ['hint_level', 'requested_at']
    search_fields = ['player__username', 'challenge__title']
    readonly_fields = ['id', 'requested_at']