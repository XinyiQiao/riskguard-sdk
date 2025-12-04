# behavioral_scanner.py
"""
Behavioral risk scanner for detecting hallucinations, toxicity, and safety violations.
Uses transformer models for NLI-based contradiction detection and toxicity classification.
All scanning happens locally - no external API calls.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, Any


class BehavioralScanner:
    """
    Local behavioral scanner for LLM outputs using ML models.
    - NLI model (facebook/bart-large-mnli) for contradiction/hallucination detection
    - Toxicity classifier (unitary/toxic-bert) for unsafe content detection
    - Uncertainty heuristics for confidence analysis
    """
    
    def __init__(self):
        print("🔄 Loading behavioral scanner models...")
        
        # NLI model for contradiction / consistency checking
        self.nli_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
        self.nli_model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")
        
        # Toxicity model for unsafe content detection
        self.tox_tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
        self.tox_model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
        
        print("✅ Behavioral scanner models loaded successfully.")
        
    def detect_hallucination(self, prompt: str, response: str) -> float:
        """
        Use NLI model to detect contradiction between prompt and response.
        High contradiction score indicates potential hallucination.
        
        Args:
            prompt: User input prompt
            response: LLM response text
            
        Returns:
            Contradiction probability (0-1)
        """
        inputs = self.nli_tokenizer(
            prompt, 
            response, 
            return_tensors="pt", 
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            logits = self.nli_model(**inputs).logits
            probs = logits.softmax(dim=1)
            # BART-MNLI: index 0 = contradiction, 1 = neutral, 2 = entailment
            contradiction_score = probs[0][0].item()
        
        return contradiction_score
    
    def detect_toxicity(self, text: str) -> float:
        """
        Use toxicity model to detect unsafe or harmful content.
        
        Args:
            text: Text to analyze (typically the response)
            
        Returns:
            Toxicity probability (0-1)
        """
        inputs = self.tox_tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            logits = self.tox_model(**inputs).logits
            probs = logits.softmax(dim=1)
            # toxic-bert: index 0 = non-toxic, 1 = toxic
            toxicity_score = probs[0][1].item()
        
        return toxicity_score
    
    def uncertainty_score(self, response: str) -> float:
        """
        Simple heuristic for uncertainty detection.
        Long, repetitive, or overconfident responses indicate higher uncertainty.
        
        Args:
            response: LLM response text
            
        Returns:
            Uncertainty score (0-1)
        """
        if not response or len(response.strip()) == 0:
            return 1.0
        
        words = response.split()
        word_count = len(words)
        
        # Repetition ratio (low = high repetition)
        unique_words = len(set(words))
        repetition_ratio = unique_words / (word_count + 1e-6)
        
        # Overconfident language indicators
        overconfident_words = [
            'definitely', 'certainly', 'undoubtedly', 'absolutely',
            'without doubt', 'guaranteed', 'always', '100%'
        ]
        overconfident_count = sum(
            1 for word in overconfident_words 
            if word in response.lower()
        )
        
        # Length factor (very long responses can indicate verbosity/uncertainty)
        length_factor = min(word_count / 100.0, 1.0)
        
        # Combined uncertainty score
        uncertainty = (
            0.2 * length_factor +                    # Long responses
            0.3 * (1 - repetition_ratio) +          # High repetition
            0.5 * min(overconfident_count / 3.0, 1.0)  # Overconfidence
        )
        
        return min(uncertainty, 1.0)
    
    def scan(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Scan prompt and response for behavioral risks using ML models.
        
        Args:
            prompt: User input prompt
            response: LLM response text
            
        Returns:
            Dictionary with behavioral risk metadata
        """
        # Use NLI model for hallucination/contradiction detection
        contradiction_score = self.detect_hallucination(prompt, response)
        
        # Use toxicity classifier
        toxicity_score = self.detect_toxicity(response)
        
        # Use heuristic for uncertainty
        uncertainty_score = self.uncertainty_score(response)
        
        # Overall behavioral risk (weighted average)
        # Higher weight on contradiction and toxicity (ML-based)
        behavioral_risk = (
            0.4 * contradiction_score +
            0.4 * toxicity_score +
            0.2 * uncertainty_score
        )
        
        return {
            'hallucination_score': round(contradiction_score, 3),
            'contradiction_score': round(contradiction_score, 3),  # alias
            'toxicity_score': round(toxicity_score, 3),
            'uncertainty_score': round(uncertainty_score, 3),
            'safety_violation_score': round(toxicity_score, 3),  # toxicity implies safety violation
            'behavioral_risk': round(behavioral_risk, 3),
            'has_behavioral_issues': behavioral_risk > 0.5
        }

