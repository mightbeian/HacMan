from celery import shared_task
from django.contrib.auth import get_user_model
from challenges.models import Challenge
from .predictor import DifficultyPredictor, TimePredictor
from .hint_generator import HintGenerator
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def update_difficulty_model(user_id=None):
    """Update the ML difficulty prediction model"""
    try:
        predictor = DifficultyPredictor()
        success = predictor.train_model(min_samples=30)
        
        if success:
            logger.info("Difficulty model updated successfully")
            return {'status': 'success', 'message': 'Model updated'}
        else:
            logger.warning("Not enough data to train model")
            return {'status': 'pending', 'message': 'Insufficient data'}
    except Exception as e:
        logger.error(f"Error updating difficulty model: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def generate_hint(challenge_id, user_id, attempts, hints_used):
    """Generate an AI-powered hint for a challenge"""
    try:
        challenge = Challenge.objects.get(id=challenge_id)
        user = User.objects.get(id=user_id)
        
        generator = HintGenerator()
        hint = generator.generate_hint(challenge, user, attempts)
        
        logger.info(f"Generated hint for user {user.username} on challenge {challenge.title}")
        
        return {
            'status': 'success',
            'hint': hint,
            'attempts': attempts
        }
    except Exception as e:
        logger.error(f"Error generating hint: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

@shared_task
def update_user_recommendations(user_id):
    """Update challenge recommendations for a user"""
    try:
        user = User.objects.get(id=user_id)
        predictor = DifficultyPredictor()
        
        recommendations = predictor.get_recommended_challenges(user, limit=15)
        
        logger.info(f"Updated recommendations for user {user.username}")
        
        return {
            'status': 'success',
            'count': len(recommendations),
            'user': user.username
        }
    except Exception as e:
        logger.error(f"Error updating recommendations: {e}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def periodic_model_training():
    """Periodic task to retrain ML models"""
    try:
        predictor = DifficultyPredictor()
        predictor.train_model(min_samples=50)
        
        logger.info("Periodic model training completed")
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Error in periodic training: {e}")
        return {'status': 'error', 'message': str(e)}
