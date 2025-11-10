from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Badge, UserBadge

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['badge', 'earned_at']

class UserProfileSerializer(serializers.ModelSerializer):
    badges = UserBadgeSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'total_points', 'rank', 
                  'avatar_url', 'bio', 'current_streak', 'longest_streak',
                  'challenges_completed', 'badges', 'created_at']
        read_only_fields = ['total_points', 'rank', 'challenges_completed']

class LeaderboardSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ['position', 'id', 'username', 'total_points', 'rank', 
                  'avatar_url', 'challenges_completed']
