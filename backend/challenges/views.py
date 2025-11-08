from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
import time

from .models import Challenge, Submission, HintRequest
from .serializers import (
    ChallengeListSerializer,
    ChallengeDetailSerializer,
    SubmissionSerializer,
    HintRequestSerializer,
    FlagSubmissionSerializer
)
from players.models import PlayerProfile
from ml_engine.services import DifficultyPredictor, HintGenerator

class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Challenge.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ChallengeListSerializer
        return ChallengeDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        difficulty = self.request.query_params.get('difficulty')
        
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit(self, request, pk=None):
        challenge = self.get_object()
        serializer = FlagSubmissionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Rate limiting check
        recent_submissions = Submission.objects.filter(
            player=request.user,
            challenge=challenge,
            submitted_at__gte=timezone.now() - timedelta(seconds=5)
        ).count()
        
        if recent_submissions > 0:
            return Response(
                {'error': 'Please wait a few seconds before submitting again.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Check if already solved
        if Submission.objects.filter(player=request.user, challenge=challenge, is_correct=True).exists():
            return Response(
                {'error': 'You have already solved this challenge.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submitted_flag = serializer.validated_data['flag']
        is_correct = challenge.verify_flag(submitted_flag)
        
        # Calculate solve time
        first_attempt = Submission.objects.filter(
            player=request.user,
            challenge=challenge
        ).order_by('submitted_at').first()
        
        solve_time = None
        if first_attempt:
            solve_time = int((timezone.now() - first_attempt.submitted_at).total_seconds())
        
        # Get hints used
        hints_used = HintRequest.objects.filter(
            player=request.user,
            challenge=challenge
        ).count()
        
        # Create submission
        submission = Submission.objects.create(
            player=request.user,
            challenge=challenge,
            submitted_flag=submitted_flag,
            is_correct=is_correct,
            solve_time_seconds=solve_time if is_correct else None,
            hints_used=hints_used
        )
        
        if is_correct:
            # Update challenge solve count
            challenge.solve_count += 1
            challenge.save()
            
            # Update player profile
            profile = PlayerProfile.objects.get(user=request.user)
            points_earned = max(challenge.points - (hints_used * 10), 10)
            profile.total_points += points_earned
            profile.challenges_solved += 1
            profile.save()
            
            return Response({
                'success': True,
                'message': 'Correct flag! Challenge solved!',
                'points_earned': points_earned,
                'solve_time': solve_time,
                'total_points': profile.total_points
            }, status=status.HTTP_200_OK)
        else:
            attempts = Submission.objects.filter(
                player=request.user,
                challenge=challenge
            ).count()
            
            return Response({
                'success': False,
                'message': 'Incorrect flag. Try again!',
                'attempts': attempts
            }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def hint(self, request, pk=None):
        challenge = self.get_object()
        
        # Check if already solved
        if Submission.objects.filter(player=request.user, challenge=challenge, is_correct=True).exists():
            return Response(
                {'error': 'You have already solved this challenge.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check hint count
        hints_used = HintRequest.objects.filter(
            player=request.user,
            challenge=challenge
        ).count()
        
        if hints_used >= 3:
            return Response(
                {'error': 'Maximum hints reached for this challenge.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hint_level = hints_used + 1
        
        # Check if hint already exists
        existing_hint = HintRequest.objects.filter(
            player=request.user,
            challenge=challenge,
            hint_level=hint_level
        ).first()
        
        if existing_hint:
            return Response({
                'hint': existing_hint.hint_text,
                'hint_level': hint_level,
                'hints_remaining': 3 - hint_level,
                'penalty_points': 10
            })
        
        # Generate hint using ML
        hint_generator = HintGenerator()
        hint_text = hint_generator.generate_hint(
            challenge.description,
            challenge.category,
            hint_level
        )
        
        # Save hint request
        hint_request = HintRequest.objects.create(
            player=request.user,
            challenge=challenge,
            hint_level=hint_level,
            hint_text=hint_text
        )
        
        return Response({
            'hint': hint_text,
            'hint_level': hint_level,
            'hints_remaining': 3 - hint_level,
            'penalty_points': 10
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommended(self, request):
        predictor = DifficultyPredictor()
        recommended_ids = predictor.get_recommendations(request.user)
        
        recommended_challenges = Challenge.objects.filter(
            id__in=recommended_ids,
            is_active=True
        )
        
        serializer = self.get_serializer(recommended_challenges, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_challenges = Challenge.objects.filter(is_active=True).count()
        
        category_stats = Challenge.objects.filter(is_active=True).values('category').annotate(
            count=Count('id'),
            avg_difficulty=Avg('difficulty')
        )
        
        difficulty_stats = Challenge.objects.filter(is_active=True).values('difficulty').annotate(
            count=Count('id')
        )
        
        return Response({
            'total_challenges': total_challenges,
            'by_category': list(category_stats),
            'by_difficulty': list(difficulty_stats)
        })