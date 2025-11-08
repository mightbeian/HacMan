from django.db import models
import uuid

class MLModel(models.Model):
    MODEL_TYPES = [
        ('difficulty', 'Difficulty Predictor'),
        ('hint', 'Hint Generator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    version = models.CharField(max_length=50)
    file_path = models.CharField(max_length=500)
    accuracy = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    trained_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-trained_at']
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"

class TrainingLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_logs')
    samples_count = models.IntegerField()
    training_accuracy = models.FloatField()
    validation_accuracy = models.FloatField()
    training_time_seconds = models.FloatField()
    parameters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Training log for {self.model.name} - {self.created_at}"