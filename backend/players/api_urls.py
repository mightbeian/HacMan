from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlayerProfileViewSet,
    dashboard_view,
    leaderboard_view,
    player_stats_view
)

router = DefaultRouter()
router.register(r'profile', PlayerProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('leaderboard/', leaderboard_view, name='leaderboard'),
    path('stats/<str:username>/', player_stats_view, name='player_stats'),
]