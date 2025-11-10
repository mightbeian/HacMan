from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Window, F
from django.db.models.functions import RowNumber

from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    LeaderboardSerializer
)

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        user = request.user
        total_users = User.objects.count()
        user_position = User.objects.filter(total_points__gt=user.total_points).count() + 1
        
        return Response({
            'total_points': user.total_points,
            'rank': user.rank,
            'position': user_position,
            'total_users': total_users,
            'challenges_completed': user.challenges_completed,
            'current_streak': user.current_streak,
            'longest_streak': user.longest_streak,
        })

class LeaderboardView(generics.ListAPIView):
    serializer_class = LeaderboardSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = User.objects.annotate(
            position=Window(
                expression=RowNumber(),
                order_by=F('total_points').desc()
            )
        ).order_by('-total_points')[:100]
        return queryset
