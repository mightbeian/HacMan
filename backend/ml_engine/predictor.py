import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
from django.conf import settings
from django.db.models import Avg, Count, Q
from challenges.models import Challenge, UserProgress, Submission
from users.models import User
from .models import UserPerformanceMetrics, MLPrediction

class DifficultyPredictor:
    def __init__(self):
        self.model_path = settings.ML_MODEL_PATH / 'difficulty_model.pkl'
        self.scaler_path = settings.ML_MODEL_PATH / 'scaler.pkl'
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load or initialize the ML model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
            else:
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                self.scaler = StandardScaler()
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.scaler = StandardScaler()
    
    def save_model(self):
        """Save the trained model"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def extract_user_features(self, user):
        """Extract features from user's performance history"""
        metrics, _ = UserPerformanceMetrics.objects.get_or_create(user=user)
        
        # Get user's solve statistics
        solved_challenges = UserProgress.objects.filter(
            user=user,
            is_solved=True
        )
        
        if solved_challenges.exists():
            avg_difficulty = solved_challenges.aggregate(
                avg_diff=Avg('challenge__difficulty')
            )['avg_diff'] or 2
            
            avg_attempts = solved_challenges.aggregate(
                avg_att=Avg('attempts')
            )['avg_att'] or 1
            
            avg_time = solved_challenges.aggregate(
                avg_t=Avg('time_spent')
            )['avg_t'] or 0
        else:
            avg_difficulty = 1
            avg_attempts = 0
            avg_time = 0
        
        # Category performance
        category_stats = {}
        for category in ['web', 'crypto', 'forensics', 'steganography', 'reverse']:
            cat_solved = solved_challenges.filter(
                challenge__category__name__icontains=category
            ).count()
            category_stats[f'{category}_solved'] = cat_solved
        
        features = {
            'total_points': user.total_points,
            'challenges_completed': user.challenges_completed,
            'avg_difficulty_solved': avg_difficulty,
            'avg_attempts': avg_attempts,
            'avg_solve_time': avg_time / 60 if avg_time else 0,
            'current_streak': user.current_streak,
            **category_stats
        }
        
        return features
    
    def extract_challenge_features(self, challenge):
        """Extract features from challenge"""
        return {
            'difficulty': challenge.difficulty,
            'points': challenge.points,
            'solve_count': challenge.solve_count,
            'success_rate': challenge.success_rate,
            'avg_completion_time': challenge.avg_completion_time / 60 if challenge.avg_completion_time else 0,
            'hint_count': len(challenge.hints),
        }
    
    def prepare_features(self, user, challenge):
        """Combine user and challenge features"""
        user_features = self.extract_user_features(user)
        challenge_features = self.extract_challenge_features(challenge)
        
        features = {**user_features, **challenge_features}
        return pd.DataFrame([features])
    
    def predict_difficulty(self, user, challenge):
        """Predict if a challenge is appropriate for the user"""
        features_df = self.prepare_features(user, challenge)
        
        if self.model and hasattr(self.model, 'predict_proba'):
            try:
                features_scaled = self.scaler.transform(features_df)
                prediction = self.model.predict_proba(features_scaled)[0]
                confidence = max(prediction)
                
                # Save prediction
                MLPrediction.objects.create(
                    user=user,
                    challenge=challenge,
                    predicted_difficulty=float(np.argmax(prediction) + 1),
                    predicted_time=challenge.avg_completion_time,
                    confidence_score=float(confidence),
                    features_used=features_df.to_dict('records')[0]
                )
                
                return {
                    'suitable': confidence > 0.6,
                    'confidence': float(confidence),
                    'predicted_difficulty': int(np.argmax(prediction) + 1)
                }
            except Exception as e:
                print(f"Prediction error: {e}")
        
        # Fallback to simple heuristic
        user_avg_diff = user.challenges_completed // 5 + 1
        suitable = abs(challenge.difficulty - user_avg_diff) <= 1
        
        return {
            'suitable': suitable,
            'confidence': 0.5,
            'predicted_difficulty': user_avg_diff
        }
    
    def get_recommended_challenges(self, user, limit=10):
        """Get recommended challenges for a user"""
        # Get unsolved challenges
        solved_ids = UserProgress.objects.filter(
            user=user,
            is_solved=True
        ).values_list('challenge_id', flat=True)
        
        available_challenges = Challenge.objects.filter(
            is_active=True
        ).exclude(id__in=solved_ids)
        
        # Score each challenge
        recommendations = []
        for challenge in available_challenges:
            prediction = self.predict_difficulty(user, challenge)
            if prediction['suitable']:
                score = prediction['confidence'] * (1.0 - challenge.success_rate / 100)
                recommendations.append({
                    'challenge': challenge,
                    'score': score,
                    'prediction': prediction
                })
        
        # Sort by score and return top challenges
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return [r['challenge'] for r in recommendations[:limit]]
    
    def train_model(self, min_samples=50):
        """Train the difficulty prediction model"""
        # Collect training data
        training_data = []
        
        solved_progress = UserProgress.objects.filter(
            is_solved=True
        ).select_related('user', 'challenge')
        
        if solved_progress.count() < min_samples:
            print(f"Not enough data for training (need {min_samples}, have {solved_progress.count()})")
            return False
        
        for progress in solved_progress:
            user_features = self.extract_user_features(progress.user)
            challenge_features = self.extract_challenge_features(progress.challenge)
            
            features = {**user_features, **challenge_features}
            
            # Label: was this challenge appropriate? (based on attempts)
            appropriate = 1 if progress.attempts <= 5 else 0
            
            training_data.append({**features, 'label': appropriate})
        
        df = pd.DataFrame(training_data)
        X = df.drop('label', axis=1)
        y = df['label']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        print(f"Model trained on {len(training_data)} samples")
        return True

class TimePredictor:
    """Predict expected completion time for challenges"""
    
    def __init__(self):
        self.model_path = settings.ML_MODEL_PATH / 'time_model.pkl'
        self.model = None
        self.load_model()
    
    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
            else:
                self.model = RandomForestRegressor(
                    n_estimators=50,
                    max_depth=8,
                    random_state=42
                )
        except Exception as e:
            print(f"Error loading time model: {e}")
            self.model = RandomForestRegressor(
                n_estimators=50,
                max_depth=8,
                random_state=42
            )
    
    def predict_time(self, user, challenge):
        """Predict expected time to solve a challenge"""
        # Simple heuristic based on user's average solve time
        user_avg = UserProgress.objects.filter(
            user=user,
            is_solved=True
        ).aggregate(avg_time=Avg('time_spent'))['avg_time']
        
        if user_avg:
            difficulty_factor = challenge.difficulty / 3
            predicted_time = user_avg * difficulty_factor
        else:
            predicted_time = challenge.avg_completion_time if challenge.avg_completion_time > 0 else 1800
        
        return int(predicted_time)
