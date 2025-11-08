from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import hashlib
import uuid

class Challenge(models.Model):
    CATEGORY_CHOICES = [
        ('web', 'Web Exploitation'),
        ('crypto', 'Cryptography'),
        ('stego', 'Steganography'),
        ('forensics', 'Forensics'),
        ('binary', 'Binary Exploitation'),
        ('misc', 'Miscellaneous'),
    ]
    
    DIFFICULTY_CHOICES = [
        (1, 'Beginner'),
        (2, 'Easy'),
        (3, 'Medium'),
        (4, 'Hard'),
        (5, 'Expert'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    points = models.IntegerField(validators=[MinValueValidator(0)])
    flag = models.CharField(max_length=500)
    flag_hash = models.CharField(max_length=64, editable=False)
    hints = models.JSONField(default=list)
    files = models.JSONField(default=list, blank=True)
    url = models.URLField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='authored_challenges')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    solve_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['difficulty', 'points']
        indexes = [
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if self.flag and not self.flag_hash:
            self.flag_hash = hashlib.sha256(self.flag.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def verify_flag(self, submitted_flag):
        submitted_hash = hashlib.sha256(submitted_flag.strip().encode()).hexdigest()
        return submitted_hash == self.flag_hash
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()}) - {self.get_difficulty_display()}"

class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    submitted_flag = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    solve_time_seconds = models.IntegerField(null=True, blank=True)
    hints_used = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['player', 'challenge', 'is_correct']),
            models.Index(fields=['submitted_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} {self.player.username} - {self.challenge.title}"

class HintRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hint_requests')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='hint_requests')
    hint_level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)])
    hint_text = models.TextField()
    requested_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['requested_at']
        unique_together = ['player', 'challenge', 'hint_level']
    
    def __str__(self):
        return f"{self.player.username} - {self.challenge.title} (Hint {self.hint_level})"