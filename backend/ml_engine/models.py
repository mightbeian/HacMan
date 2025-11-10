from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserPerformanceMetrics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metrics')
    avg_solve_time = models.FloatField(default=0.0)
    avg_attempts_per_challenge = models.FloatField(default=0.0)
    preferred_categories = models.JSONField(default=list)
    skill_levels = models.JSONField(default=dict)
    learning_rate = models.FloatField(default=1.0)
    difficulty_preference = models.IntegerField(default=2)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'User Performance Metrics'
    
    def __str__(self):
        return f"{self.user.username} - Metrics"

class MLPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey('challenges.Challenge', on_delete=models.CASCADE)
    predicted_difficulty = models.FloatField()
    predicted_time = models.FloatField()
    confidence_score = models.FloatField()
    features_used = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} prediction"
