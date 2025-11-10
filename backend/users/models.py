from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    total_points = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rank = models.CharField(max_length=50, default='Beginner')
    avatar_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    challenges_completed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-total_points']
        indexes = [
            models.Index(fields=['-total_points']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return self.username
    
    def update_rank(self):
        """Update user rank based on total points"""
        if self.total_points < 100:
            self.rank = 'Beginner'
        elif self.total_points < 500:
            self.rank = 'Novice'
        elif self.total_points < 1000:
            self.rank = 'Intermediate'
        elif self.total_points < 2500:
            self.rank = 'Advanced'
        elif self.total_points < 5000:
            self.rank = 'Expert'
        elif self.total_points < 10000:
            self.rank = 'Master'
        else:
            self.rank = 'Legend'
        self.save()

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    requirement_type = models.CharField(max_length=50)
    requirement_value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
