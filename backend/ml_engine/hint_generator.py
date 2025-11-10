import os
from typing import Dict, List
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from challenges.models import Challenge, UserProgress
from users.models import User

class HintGenerator:
    """Generate contextual hints using NLP models"""
    
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.summarizer = None
        self.initialized = False
    
    def initialize(self):
        """Lazy load the model"""
        if not self.initialized:
            try:
                # Use a smaller model for hint generation
                model_name = "facebook/bart-large-cnn"
                self.summarizer = pipeline(
                    "summarization",
                    model=model_name,
                    device=self.device
                )
                self.initialized = True
            except Exception as e:
                print(f"Error initializing hint generator: {e}")
                self.initialized = False
    
    def generate_hint(self, challenge: Challenge, user: User, attempt_number: int) -> str:
        """Generate a contextual hint based on challenge and user progress"""
        
        # Get user progress
        try:
            progress = UserProgress.objects.get(user=user, challenge=challenge)
        except UserProgress.DoesNotExist:
            progress = None
        
        # Determine hint level based on attempts
        if attempt_number <= 2:
            hint_level = "basic"
        elif attempt_number <= 5:
            hint_level = "intermediate"
        else:
            hint_level = "advanced"
        
        # Generate contextual hint
        hints = self._generate_progressive_hints(challenge, hint_level, progress)
        
        return hints
    
    def _generate_progressive_hints(self, challenge: Challenge, level: str, progress) -> str:
        """Generate progressive hints based on difficulty and category"""
        
        category = challenge.category.name.lower()
        difficulty = challenge.difficulty
        
        # Template-based hints for different categories
        hint_templates = {
            "web": {
                "basic": "Look for common web vulnerabilities. Check the page source and inspect HTTP requests.",
                "intermediate": f"Focus on {self._get_web_hint(difficulty)}. Try using developer tools.",
                "advanced": "Consider SQL injection, XSS, or CSRF. Check authentication mechanisms."
            },
            "crypto": {
                "basic": "Analyze the encryption pattern. Look for common cipher types.",
                "intermediate": "Consider frequency analysis or known-plaintext attacks.",
                "advanced": "Try modern cryptanalysis techniques or look for implementation flaws."
            },
            "forensics": {
                "basic": "Examine file headers and metadata. Use forensic tools to extract hidden data.",
                "intermediate": "Look for steganography, deleted files, or hidden partitions.",
                "advanced": "Perform memory analysis or timeline reconstruction."
            },
            "steganography": {
                "basic": "Something might be hidden in plain sight. Check image properties.",
                "intermediate": "Try LSB analysis or spectral analysis tools.",
                "advanced": "Consider audio steganography or complex encoding schemes."
            },
            "reverse": {
                "basic": "Use a disassembler or decompiler to understand the code.",
                "intermediate": "Look for interesting strings, functions, or anti-debugging techniques.",
                "advanced": "Analyze the algorithm, patch protections, or perform dynamic analysis."
            }
        }
        
        # Get appropriate category (fallback to web if not found)
        category_key = None
        for key in hint_templates.keys():
            if key in category:
                category_key = key
                break
        
        if not category_key:
            category_key = "web"
        
        base_hint = hint_templates[category_key].get(level, hint_templates[category_key]["basic"])
        
        # Add context based on user progress
        if progress and progress.attempts > 3:
            base_hint += " You're making progress - review your previous attempts."
        
        return base_hint
    
    def _get_web_hint(self, difficulty: int) -> str:
        """Get specific web vulnerability hints based on difficulty"""
        hints = {
            1: "basic input validation and URL parameters",
            2: "cookie manipulation or session handling",
            3: "SQL injection or command injection",
            4: "advanced XSS or CSRF attacks",
            5: "complex vulnerability chains or race conditions"
        }
        return hints.get(difficulty, "common web vulnerabilities")
    
    def generate_educational_hint(self, challenge: Challenge, concept: str) -> str:
        """Generate educational hints explaining concepts"""
        
        educational_content = {
            "sql_injection": "SQL Injection occurs when user input is directly concatenated into SQL queries. Use parameterized queries to prevent this.",
            "xss": "Cross-Site Scripting (XSS) allows attackers to inject malicious scripts. Always sanitize user input and use Content Security Policy.",
            "buffer_overflow": "Buffer overflows occur when data exceeds allocated memory. Modern protections include ASLR, DEP, and stack canaries.",
            "cryptography": "Strong encryption requires proper key management, secure algorithms, and protection against side-channel attacks.",
            "steganography": "Steganography hides data within other data. Look for LSB modifications, metadata, or unusual file properties.",
        }
        
        return educational_content.get(concept, "Research the topic and try different approaches.")
    
    def summarize_solution(self, solution_text: str) -> str:
        """Summarize a solution into a brief hint"""
        if not self.initialized:
            self.initialize()
        
        if not self.initialized or not solution_text:
            return "Review the challenge description carefully."
        
        try:
            summary = self.summarizer(
                solution_text,
                max_length=100,
                min_length=30,
                do_sample=False
            )
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing: {e}")
            return "Consider the key concepts related to this challenge category."
