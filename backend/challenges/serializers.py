from rest_framework import serializers
from .models import Challenge, Submission, HintRequest
from django.contrib.auth.models import User

class ChallengeListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    is_solved = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = ['id', 'title', 'category', 'difficulty', 'points', 'solve_count', 
                  'author_username', 'is_solved', 'created_at']
    
    def get_is_solved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                player=request.user,
                challenge=obj,
                is_correct=True
            ).exists()
        return False

class ChallengeDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    is_solved = serializers.SerializerMethodField()
    hints_used = serializers.SerializerMethodField()
    submission_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = ['id', 'title', 'description', 'category', 'difficulty', 'points',
                  'files', 'url', 'author_username', 'is_solved', 'hints_used',
                  'submission_count', 'solve_count', 'created_at', 'updated_at']
        read_only_fields = ['solve_count', 'created_at', 'updated_at']
    
    def get_is_solved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                player=request.user,
                challenge=obj,
                is_correct=True
            ).exists()
        return False
    
    def get_hints_used(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return HintRequest.objects.filter(
                player=request.user,
                challenge=obj
            ).count()
        return 0
    
    def get_submission_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Submission.objects.filter(
                player=request.user,
                challenge=obj
            ).count()
        return 0

class SubmissionSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    player_username = serializers.CharField(source='player.username', read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'challenge', 'challenge_title', 'player_username',
                  'submitted_flag', 'is_correct', 'submitted_at', 'solve_time_seconds',
                  'hints_used']
        read_only_fields = ['player', 'is_correct', 'submitted_at']

class HintRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HintRequest
        fields = ['id', 'challenge', 'hint_level', 'hint_text', 'requested_at']
        read_only_fields = ['player', 'hint_text', 'requested_at']

class FlagSubmissionSerializer(serializers.Serializer):
    flag = serializers.CharField(max_length=500, required=True)
    
    def validate_flag(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Flag cannot be empty.")
        return value.strip()