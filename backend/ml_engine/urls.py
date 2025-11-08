from django.urls import path
from .views import train_models_view, model_stats_view

urlpatterns = [
    path('train/', train_models_view, name='train_models'),
    path('stats/', model_stats_view, name='model_stats'),
]