from rest_framework import serializers
from .models import Category, Challenge, Submission, UserProgress, HintRequest

class CategorySerializer(serializers.ModelSerializer):
    challenge_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color', 'challenge_count']
    
    def get_challenge_count(self, obj):
        return obj.challenges.filter(is_active=True).count()

class ChallengeListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    is_solved = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = ['id', 'title', 'category_name', 'difficulty', 'difficulty_display',
                  'points', 'tags', 'solve_count', 'success_rate', 'is_solved']
    
    def get_is_solved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserProgress.objects.filter(
                user=request.user,
                challenge=obj,
                is_solved=True
            ).exists()
        return False

class ChallengeDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    hints = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Challenge
        fields = ['id', 'title', 'description', 'category', 'difficulty', 
                  'difficulty_display', 'points', 'hints', 'files', 'tags',
                  'solve_count', 'success_rate', 'avg_completion_time',
                  'user_progress', 'created_at']
    
    def get_hints(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
        
        hint_requests = HintRequest.objects.filter(
            user=request.user,
            challenge=obj
        ).values_list('hint_index', flat=True)
        
        unlocked_hints = []
        for idx in hint_requests:
            if idx < len(obj.hints):
                unlocked_hints.append({
                    'index': idx,
                    'text': obj.hints[idx]['text'],
                    'cost': obj.hints[idx].get('cost', 0)
                })
        return unlocked_hints
    
    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        try:
            progress = UserProgress.objects.get(user=request.user, challenge=obj)
            return {
                'is_solved': progress.is_solved,
                'attempts': progress.attempts,
                'hints_used': progress.hints_used,
                'time_spent': progress.time_spent,
            }
        except UserProgress.DoesNotExist:
            return None

class SubmissionSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = ['id', 'challenge', 'challenge_title', 'flag_submitted', 
                  'is_correct', 'time_taken', 'hints_used', 'submitted_at']
        read_only_fields = ['is_correct', 'submitted_at']

class SubmitFlagSerializer(serializers.Serializer):
    flag = serializers.CharField(max_length=200)
    time_taken = serializers.IntegerField(required=False, min_value=0)

class HintRequestSerializer(serializers.ModelSerializer):
    hint_text = serializers.SerializerMethodField()
    
    class Meta:
        model = HintRequest
        fields = ['id', 'challenge', 'hint_index', 'hint_text', 'requested_at']
    
    def get_hint_text(self, obj):
        if obj.hint_index < len(obj.challenge.hints):
            return obj.challenge.hints[obj.hint_index]['text']
        return None
