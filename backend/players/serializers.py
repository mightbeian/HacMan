from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PlayerProfile, PlayerStatistics
from challenges.models import Submission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class PlayerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = PlayerProfile
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'total_points',
                  'challenges_solved', 'rank', 'badges', 'web_solved', 'crypto_solved',
                  'stego_solved', 'forensics_solved', 'binary_solved', 'created_at']
        read_only_fields = ['id', 'total_points', 'challenges_solved', 'rank',
                           'badges', 'created_at']

class PlayerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStatistics
        fields = ['avg_solve_time', 'fastest_solve', 'slowest_solve',
                  'total_hints_used', 'avg_hints_per_challenge',
                  'total_attempts', 'successful_attempts', 'failed_attempts',
                  'web_skill_level', 'crypto_skill_level', 'stego_skill_level',
                  'forensics_skill_level', 'binary_skill_level', 'last_updated']

class LeaderboardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    
    class Meta:
        model = PlayerProfile
        fields = ['username', 'total_points', 'challenges_solved', 'rank']

class DashboardSerializer(serializers.Serializer):
    profile = PlayerProfileSerializer()
    statistics = PlayerStatisticsSerializer()
    recent_solves = serializers.ListField()
    category_breakdown = serializers.DictField()
    progress_chart = serializers.ListField()