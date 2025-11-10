from django.contrib import admin
from .models import Category, Challenge, Submission, UserProgress, HintRequest

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'points', 'solve_count', 'is_active']
    list_filter = ['category', 'difficulty', 'is_active']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['solve_count', 'attempt_count', 'success_rate', 'avg_completion_time']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'category', 'difficulty', 'points', 'is_active')
        }),
        ('Challenge Data', {
            'fields': ('flag', 'hints', 'files', 'tags', 'solution_text')
        }),
        ('Statistics', {
            'fields': ('solve_count', 'attempt_count', 'success_rate', 'avg_completion_time'),
            'classes': ('collapse',)
        }),
        ('Meta', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'is_correct', 'time_taken', 'submitted_at']
    list_filter = ['is_correct', 'submitted_at']
    search_fields = ['user__username', 'challenge__title']
    readonly_fields = ['submitted_at']

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'is_solved', 'attempts', 'hints_used']
    list_filter = ['is_solved']
    search_fields = ['user__username', 'challenge__title']

@admin.register(HintRequest)
class HintRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'hint_index', 'requested_at']
    list_filter = ['requested_at']
    search_fields = ['user__username', 'challenge__title']
