from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Count, Avg, Sum
from datetime import timedelta
from django.utils import timezone

from .models import PlayerProfile, PlayerStatistics
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    PlayerProfileSerializer,
    PlayerStatisticsSerializer,
    LeaderboardSerializer,
    DashboardSerializer
)
from challenges.models import Submission, Challenge

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class PlayerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PlayerProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        profile = request.user.profile
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    profile = user.profile
    statistics = user.statistics
    
    # Recent solves (last 10)
    recent_solves = Submission.objects.filter(
        player=user,
        is_correct=True
    ).select_related('challenge').order_by('-submitted_at')[:10]
    
    recent_solves_data = [{
        'challenge': solve.challenge.title,
        'category': solve.challenge.category,
        'points': solve.challenge.points,
        'solved_at': solve.submitted_at,
        'solve_time': solve.solve_time_seconds
    } for solve in recent_solves]
    
    # Category breakdown
    category_breakdown = {
        'web': profile.web_solved,
        'crypto': profile.crypto_solved,
        'stego': profile.stego_solved,
        'forensics': profile.forensics_solved,
        'binary': profile.binary_solved,
    }
    
    # Progress chart (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    progress_data = []
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        next_date = date + timedelta(days=1)
        
        points = Submission.objects.filter(
            player=user,
            is_correct=True,
            submitted_at__gte=date,
            submitted_at__lt=next_date
        ).aggregate(total=Sum('challenge__points'))['total'] or 0
        
        progress_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'points': points
        })
    
    data = {
        'profile': PlayerProfileSerializer(profile).data,
        'statistics': PlayerStatisticsSerializer(statistics).data,
        'recent_solves': recent_solves_data,
        'category_breakdown': category_breakdown,
        'progress_chart': progress_data
    }
    
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard_view(request):
    top_players = PlayerProfile.objects.select_related('user').order_by('-total_points')[:100]
    serializer = LeaderboardSerializer(top_players, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def player_stats_view(request, username):
    try:
        user = User.objects.get(username=username)
        profile = user.profile
        statistics = user.statistics
        
        # Challenge solves by category
        category_stats = Submission.objects.filter(
            player=user,
            is_correct=True
        ).values('challenge__category').annotate(
            count=Count('id'),
            avg_time=Avg('solve_time_seconds')
        )
        
        data = {
            'profile': PlayerProfileSerializer(profile).data,
            'statistics': PlayerStatisticsSerializer(statistics).data,
            'category_stats': list(category_stats)
        }
        
        return Response(data)
    except User.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )