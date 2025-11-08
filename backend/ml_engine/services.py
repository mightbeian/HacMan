import numpy as np
import pickle
import os
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from django.contrib.auth.models import User
from challenges.models import Challenge, Submission
from players.models import PlayerStatistics

class DifficultyPredictor:
    """
    ML model to predict optimal challenge difficulty for a player
    based on their performance history.
    """
    
    def __init__(self):
        self.model_path = settings.DIFFICULTY_MODEL_PATH
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
        except Exception as e:
            print(f"Error loading difficulty model: {e}")
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Initialize a default model if none exists"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
    
    def extract_features(self, user):
        """
        Extract feature vector from user's performance data
        
        Features:
        - Total challenges solved
        - Average solve time
        - Hint usage rate
        - Success rate
        - Category-specific skill levels
        """
        try:
            stats = user.statistics
            profile = user.profile
            
            # Calculate success rate
            total_attempts = stats.total_attempts if stats.total_attempts > 0 else 1
            success_rate = stats.successful_attempts / total_attempts
            
            # Calculate hint usage rate
            challenges_solved = profile.challenges_solved if profile.challenges_solved > 0 else 1
            hint_rate = stats.total_hints_used / challenges_solved
            
            features = [
                profile.challenges_solved,
                stats.avg_solve_time / 3600,  # Convert to hours
                hint_rate,
                success_rate,
                stats.web_skill_level,
                stats.crypto_skill_level,
                stats.stego_skill_level,
                stats.forensics_skill_level,
                stats.binary_skill_level,
            ]
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            print(f"Error extracting features: {e}")
            # Return default beginner features
            return np.array([0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0]).reshape(1, -1)
    
    def predict_difficulty(self, user, category=None):
        """
        Predict optimal difficulty level for user
        Returns difficulty level (1-5)
        """
        if self.model is None:
            # Default to easy for new users
            return 2
        
        try:
            features = self.extract_features(user)
            
            # If scaler is trained, use it
            if self.scaler is not None:
                features = self.scaler.transform(features)
            
            # Predict difficulty
            difficulty = self.model.predict(features)[0]
            
            # Adjust based on category-specific skill if provided
            if category:
                stats = user.statistics
                category_skills = {
                    'web': stats.web_skill_level,
                    'crypto': stats.crypto_skill_level,
                    'stego': stats.stego_skill_level,
                    'forensics': stats.forensics_skill_level,
                    'binary': stats.binary_skill_level,
                }
                
                skill = category_skills.get(category, 1.0)
                difficulty = min(5, max(1, int(difficulty + skill - 2)))
            
            return int(difficulty)
        except Exception as e:
            print(f"Error predicting difficulty: {e}")
            return 2
    
    def get_recommendations(self, user, count=5):
        """
        Get recommended challenges for user based on predicted difficulty
        """
        # Get solved challenge IDs
        solved_ids = Submission.objects.filter(
            player=user,
            is_correct=True
        ).values_list('challenge_id', flat=True)
        
        # Predict optimal difficulty for each category
        recommendations = []
        categories = ['web', 'crypto', 'stego', 'forensics', 'binary']
        
        for category in categories:
            difficulty = self.predict_difficulty(user, category)
            
            # Find challenges in this category and difficulty
            challenges = Challenge.objects.filter(
                category=category,
                difficulty__gte=max(1, difficulty - 1),
                difficulty__lte=min(5, difficulty + 1),
                is_active=True
            ).exclude(
                id__in=solved_ids
            ).order_by('?')[:2]
            
            recommendations.extend([c.id for c in challenges])
        
        return recommendations[:count]
    
    def train(self, training_data):
        """
        Train the difficulty prediction model
        
        training_data: List of (features, difficulty_label) tuples
        """
        if not training_data:
            print("No training data available")
            return
        
        try:
            X = np.array([item[0] for item in training_data])
            y = np.array([item[1] for item in training_data])
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_scaled, y)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler
                }, f)
            
            print(f"Model trained and saved to {self.model_path}")
        except Exception as e:
            print(f"Error training model: {e}")

class HintGenerator:
    """
    NLP-based hint generator using rule-based and template approaches
    For production, this could be replaced with a fine-tuned BERT model
    """
    
    def __init__(self):
        self.category_hints = {
            'web': [
                "Start by examining the page source and looking for comments or hidden fields.",
                "Consider common web vulnerabilities like SQL injection or XSS.",
                "Try using developer tools to inspect network requests and responses."
            ],
            'crypto': [
                "Identify the type of cipher or encryption used first.",
                "Look for patterns in the ciphertext that might reveal the encryption method.",
                "Consider classical ciphers like Caesar, Vigenère, or substitution ciphers."
            ],
            'stego': [
                "Check the file metadata and properties first.",
                "Consider using tools like steghide, binwalk, or strings.",
                "Look for LSB steganography or hidden data in image channels."
            ],
            'forensics': [
                "Start by identifying the file type and examining its structure.",
                "Use tools like strings, file, and binwalk to analyze the data.",
                "Look for deleted files, hidden partitions, or memory artifacts."
            ],
            'binary': [
                "Begin with static analysis using tools like strings or file.",
                "Consider using a disassembler like Ghidra or IDA to reverse engineer.",
                "Look for common vulnerabilities like buffer overflows or format strings."
            ]
        }
        
        self.generic_hints = [
            "Read the challenge description carefully for clues.",
            "Research the technologies or concepts mentioned in the challenge.",
            "Break the problem down into smaller, manageable steps."
        ]
    
    def generate_hint(self, description, category, hint_level):
        """
        Generate a hint based on challenge description and category
        
        hint_level: 1 (vague) to 3 (specific)
        """
        hints = self.category_hints.get(category, self.generic_hints)
        
        if hint_level <= len(hints):
            return hints[hint_level - 1]
        else:
            return "Consider exploring alternative approaches or researching related techniques."
    
    def extract_keywords(self, text):
        """
        Extract key technical terms from challenge description
        This is a simple implementation; could be enhanced with NLP
        """
        keywords = []
        common_terms = [
            'sql', 'xss', 'csrf', 'injection', 'buffer', 'overflow',
            'encryption', 'cipher', 'hash', 'steganography', 'metadata',
            'forensics', 'memory', 'binary', 'reverse', 'exploit'
        ]
        
        text_lower = text.lower()
        for term in common_terms:
            if term in text_lower:
                keywords.append(term)
        
        return keywords