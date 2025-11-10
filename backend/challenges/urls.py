from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ChallengeViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'challenges', ChallengeViewSet, basename='challenge')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]
