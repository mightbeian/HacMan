from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ml_engine.services import DifficultyPredictor
from challenges.models import Submission
from players.models import PlayerStatistics
import random

class Command(BaseCommand):
    help = 'Train ML models for difficulty prediction'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Training difficulty prediction model...')
        
        predictor = DifficultyPredictor()
        training_data = []
        
        # Collect training data from existing submissions
        users = User.objects.filter(submissions__is_correct=True).distinct()
        
        if users.count() < 10:
            self.stdout.write(self.style.WARNING(
                'Not enough training data. Generating synthetic data...'
            ))
            training_data = self._generate_synthetic_data()
        else:
            for user in users:
                try:
                    features = predictor.extract_features(user)
                    
                    # Get average difficulty of solved challenges
                    solved_submissions = Submission.objects.filter(
                        player=user,
                        is_correct=True
                    )
                    
                    if solved_submissions.exists():
                        avg_difficulty = sum(
                            s.challenge.difficulty for s in solved_submissions
                        ) / solved_submissions.count()
                        
                        training_data.append((features[0], int(avg_difficulty)))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f'Error processing user {user.username}: {e}'
                    ))
        
        if training_data:
            predictor.train(training_data)
            self.stdout.write(self.style.SUCCESS(
                f'Successfully trained model with {len(training_data)} samples'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                'No training data available'
            ))
    
    def _generate_synthetic_data(self, count=100):
        """Generate synthetic training data for initial model"""
        data = []
        
        for _ in range(count):
            # Random player features
            challenges_solved = random.randint(0, 50)
            avg_solve_time = random.uniform(0.1, 10)  # hours
            hint_rate = random.uniform(0, 2)
            success_rate = random.uniform(0.3, 1.0)
            
            # Category skills
            web_skill = random.uniform(1, 5)
            crypto_skill = random.uniform(1, 5)
            stego_skill = random.uniform(1, 5)
            forensics_skill = random.uniform(1, 5)
            binary_skill = random.uniform(1, 5)
            
            features = [
                challenges_solved,
                avg_solve_time,
                hint_rate,
                success_rate,
                web_skill,
                crypto_skill,
                stego_skill,
                forensics_skill,
                binary_skill,
            ]
            
            # Determine difficulty based on features
            avg_skill = (web_skill + crypto_skill + stego_skill + 
                        forensics_skill + binary_skill) / 5
            
            if avg_skill < 2:
                difficulty = 1
            elif avg_skill < 2.5:
                difficulty = 2
            elif avg_skill < 3.5:
                difficulty = 3
            elif avg_skill < 4.5:
                difficulty = 4
            else:
                difficulty = 5
            
            data.append((features, difficulty))
        
        return data