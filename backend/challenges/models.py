from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#3B82F6')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
        (4, 'Expert'),
        (5, 'Insane'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='challenges')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    points = models.IntegerField(validators=[MinValueValidator(0)])
    flag = models.CharField(max_length=200)
    hints = models.JSONField(default=list)
    files = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    solution_text = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ML tracking fields
    avg_completion_time = models.FloatField(default=0.0)
    success_rate = models.FloatField(default=0.0)
    attempt_count = models.IntegerField(default=0)
    solve_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['difficulty', '-points']
        indexes = [
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"
    
    def update_stats(self):
        """Update challenge statistics"""
        if self.attempt_count > 0:
            self.success_rate = (self.solve_count / self.attempt_count) * 100
        self.save()

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    flag_submitted = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    time_taken = models.IntegerField(help_text='Time taken in seconds', null=True, blank=True)
    hints_used = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['user', 'challenge', 'is_correct']),
            models.Index(fields=['-submitted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - {'✓' if self.is_correct else '✗'}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    is_solved = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0, help_text='Total time spent in seconds')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # ML features
    avg_time_per_attempt = models.FloatField(default=0.0)
    error_patterns = models.JSONField(default=list)
    
    class Meta:
        unique_together = ['user', 'challenge']
        verbose_name_plural = 'User Progress'
        indexes = [
            models.Index(fields=['user', 'is_solved']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title}"

class HintRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    hint_index = models.IntegerField()
    requested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} - Hint {self.hint_index}"
