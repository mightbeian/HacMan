from django.contrib import admin
from .models import MLModel, TrainingLog

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'accuracy', 'is_active', 'trained_at']
    list_filter = ['model_type', 'is_active', 'trained_at']
    search_fields = ['name', 'version']
    readonly_fields = ['id', 'trained_at']

@admin.register(TrainingLog)
class TrainingLogAdmin(admin.ModelAdmin):
    list_display = ['model', 'samples_count', 'training_accuracy', 'validation_accuracy', 'created_at']
    list_filter = ['created_at', 'model__model_type']
    readonly_fields = ['id', 'created_at']