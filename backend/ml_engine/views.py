from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from .services import DifficultyPredictor
from .models import MLModel, TrainingLog
from django.core.management import call_command

@api_view(['POST'])
@permission_classes([IsAdminUser])
def train_models_view(request):
    """
    Endpoint to trigger model training (admin only)
    """
    try:
        call_command('train_models')
        return Response({
            'success': True,
            'message': 'Model training completed successfully'
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def model_stats_view(request):
    """
    Get statistics about ML models (admin only)
    """
    models = MLModel.objects.filter(is_active=True)
    
    stats = []
    for model in models:
        latest_log = model.training_logs.first()
        
        stats.append({
            'name': model.name,
            'type': model.get_model_type_display(),
            'version': model.version,
            'accuracy': model.accuracy,
            'trained_at': model.trained_at,
            'latest_training': {
                'samples': latest_log.samples_count if latest_log else None,
                'accuracy': latest_log.validation_accuracy if latest_log else None,
                'date': latest_log.created_at if latest_log else None,
            } if latest_log else None
        })
    
    return Response({
        'models': stats
    })