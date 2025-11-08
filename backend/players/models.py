from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class PlayerProfile(models.Model):
    RANK_CHOICES = [
        ('newbie', 'Newbie'),
        ('apprentice', 'Apprentice'),
        ('hacker', 'Hacker'),
        ('expert', 'Expert'),
        ('elite', 'Elite'),
        ('legend', 'Legend'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    total_points = models.IntegerField(default=0)
    challenges_solved = models.IntegerField(default=0)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='newbie')
    badges = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Category-specific stats
    web_solved = models.IntegerField(default=0)
    crypto_solved = models.IntegerField(default=0)
    stego_solved = models.IntegerField(default=0)
    forensics_solved = models.IntegerField(default=0)
    binary_solved = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-total_points']
    
    def update_rank(self):
        if self.total_points < 100:
            self.rank = 'newbie'
        elif self.total_points < 500:
            self.rank = 'apprentice'
        elif self.total_points < 1500:
            self.rank = 'hacker'
        elif self.total_points < 3000:
            self.rank = 'expert'
        elif self.total_points < 5000:
            self.rank = 'elite'
        else:
            self.rank = 'legend'
        self.save()
    
    def award_badge(self, badge_name):
        if badge_name not in self.badges:
            self.badges.append(badge_name)
            self.save()
    
    def __str__(self):
        return f"{self.user.username} ({self.rank}) - {self.total_points} points"

@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    if created:
        PlayerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_player_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class PlayerStatistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.OneToOneField(User, on_delete=models.CASCADE, related_name='statistics')
    
    # Performance metrics
    avg_solve_time = models.FloatField(default=0.0)
    fastest_solve = models.IntegerField(null=True, blank=True)
    slowest_solve = models.IntegerField(null=True, blank=True)
    
    # Hint usage
    total_hints_used = models.IntegerField(default=0)
    avg_hints_per_challenge = models.FloatField(default=0.0)
    
    # Attempt metrics
    total_attempts = models.IntegerField(default=0)
    successful_attempts = models.IntegerField(default=0)
    failed_attempts = models.IntegerField(default=0)
    
    # Category performance (1-5 scale)
    web_skill_level = models.FloatField(default=1.0)
    crypto_skill_level = models.FloatField(default=1.0)
    stego_skill_level = models.FloatField(default=1.0)
    forensics_skill_level = models.FloatField(default=1.0)
    binary_skill_level = models.FloatField(default=1.0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Stats for {self.player.username}"

@receiver(post_save, sender=User)
def create_player_statistics(sender, instance, created, **kwargs):
    if created:
        PlayerStatistics.objects.create(player=instance)