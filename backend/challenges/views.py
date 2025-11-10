from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Challenge, Submission, UserProgress, HintRequest
from .serializers import (
    CategorySerializer,
    ChallengeListSerializer,
    ChallengeDetailSerializer,
    SubmissionSerializer,
    SubmitFlagSerializer,
    HintRequestSerializer
)
from users.models import User
from ml_engine.tasks import update_difficulty_model, generate_hint

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['difficulty', 'points', 'solve_count', 'created_at']
    
    def get_queryset(self):
        return Challenge.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChallengeDetailSerializer
        return ChallengeListSerializer
    
    @action(detail=True, methods=['post'])
    def submit_flag(self, request, pk=None):
        challenge = self.get_object()
        serializer = SubmitFlagSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        submitted_flag = serializer.validated_data['flag']
        time_taken = serializer.validated_data.get('time_taken', 0)
        
        # Get or create user progress
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge
        )
        
        progress.attempts += 1
        progress.time_spent += time_taken
        
        is_correct = submitted_flag.strip() == challenge.flag.strip()
        
        # Create submission record
        submission = Submission.objects.create(
            user=request.user,
            challenge=challenge,
            flag_submitted=submitted_flag,
            is_correct=is_correct,
            time_taken=time_taken,
            hints_used=progress.hints_used
        )
        
        challenge.attempt_count += 1
        
        if is_correct and not progress.is_solved:
            # First time solving
            progress.is_solved = True
            progress.completed_at = timezone.now()
            challenge.solve_count += 1
            
            # Award points
            points_awarded = challenge.points - (progress.hints_used * 10)
            points_awarded = max(points_awarded, challenge.points // 4)
            
            request.user.total_points += points_awarded
            request.user.challenges_completed += 1
            request.user.update_rank()
            request.user.save()
            
            # Update challenge stats
            if challenge.solve_count == 1:
                challenge.avg_completion_time = time_taken
            else:
                challenge.avg_completion_time = (
                    (challenge.avg_completion_time * (challenge.solve_count - 1) + time_taken) 
                    / challenge.solve_count
                )
            
            # Trigger ML model update
            update_difficulty_model.delay(request.user.id)
            
            response_data = {
                'success': True,
                'message': 'Congratulations! Flag is correct!',
                'points_awarded': points_awarded,
                'total_points': request.user.total_points,
                'new_rank': request.user.rank,
            }
        elif is_correct:
            response_data = {
                'success': True,
                'message': 'Flag is correct, but you already solved this challenge.',
            }
        else:
            response_data = {
                'success': False,
                'message': 'Incorrect flag. Try again!',
                'attempts': progress.attempts,
            }
        
        progress.save()
        challenge.update_stats()
        challenge.save()
        
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def request_hint(self, request, pk=None):
        challenge = self.get_object()
        
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            challenge=challenge
        )
        
        next_hint_index = progress.hints_used
        
        if next_hint_index >= len(challenge.hints):
            return Response(
                {'error': 'No more hints available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create hint request
        hint_request = HintRequest.objects.create(
            user=request.user,
            challenge=challenge,
            hint_index=next_hint_index
        )
        
        progress.hints_used += 1
        progress.save()
        
        hint_data = challenge.hints[next_hint_index]
        
        return Response({
            'hint': hint_data['text'],
            'cost': hint_data.get('cost', 0),
            'hints_remaining': len(challenge.hints) - progress.hints_used
        })
    
    @action(detail=True, methods=['post'])
    def generate_ai_hint(self, request, pk=None):
        """Generate an AI-powered hint based on user's progress"""
        challenge = self.get_object()
        
        progress = UserProgress.objects.filter(
            user=request.user,
            challenge=challenge
        ).first()
        
        if not progress:
            return Response(
                {'error': 'Start the challenge first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Async task to generate hint
        result = generate_hint.delay(
            challenge.id,
            request.user.id,
            progress.attempts,
            progress.hints_used
        )
        
        return Response({
            'message': 'Generating AI hint...',
            'task_id': result.id
        })
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get AI-recommended challenges for the user"""
        from ml_engine.predictor import DifficultyPredictor
        
        predictor = DifficultyPredictor()
        recommended_challenges = predictor.get_recommended_challenges(request.user)
        
        serializer = self.get_serializer(recommended_challenges, many=True)
        return Response(serializer.data)

class SubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)
