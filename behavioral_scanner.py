# behavioral_scanner.py
"""
Behavioral risk scanner for detecting hallucinations, toxicity, and safety violations.
All scanning happens locally - no external API calls.
"""

import re
from typing import Dict, Any


class BehavioralScanner:
    """
    Lightweight local behavioral scanner for LLM outputs.
    Detects hallucination signals, toxicity, and safety violations.
    """
    
    def __init__(self):
        # Toxicity/harmful content patterns
        self.toxic_patterns = [
            r'\b(hate|stupid|idiot|kill|die|attack)\b',
            r'\b(fuck|shit|damn|hell)\b',
        ]
        
        # Safety violation keywords
        self.unsafe_keywords = [
            'violence', 'weapon', 'bomb', 'suicide', 'murder',
            'illegal', 'hack', 'steal', 'fraud', 'scam'
        ]
        
        # Uncertainty indicators (hallucination signals)
        self.uncertainty_phrases = [
            'i think', 'maybe', 'probably', 'possibly', 'might be',
            'i\'m not sure', 'unclear', 'uncertain', 'could be'
        ]
        
    def scan(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Scan prompt and response for behavioral risks.
        
        Args:
            prompt: User input prompt
            response: LLM response text
            
        Returns:
            Dictionary with behavioral risk metadata
        """
        # Scan response for various signals
        hallucination_score = self._detect_hallucination_signals(response)
        toxicity_score = self._detect_toxicity(response)
        safety_violation_score = self._detect_safety_violations(prompt, response)
        
        # Overall behavioral risk (weighted average)
        behavioral_risk = (
            0.4 * hallucination_score +
            0.35 * toxicity_score +
            0.25 * safety_violation_score
        )
        
        return {
            'hallucination_score': round(hallucination_score, 3),
            'toxicity_score': round(toxicity_score, 3),
            'safety_violation_score': round(safety_violation_score, 3),
            'behavioral_risk': round(behavioral_risk, 3),
            'has_behavioral_issues': behavioral_risk > 0.5
        }
    
    def _detect_hallucination_signals(self, text: str) -> float:
        """
        Detect hallucination/incorrectness signals using heuristics.
        
        Signals:
        - Excessive uncertainty phrases
        - Very short responses (potential evasion)
        - Excessive repetition
        - Contradictory statements
        """
        if not text or len(text.strip()) == 0:
            return 1.0  # Empty response is suspicious
        
        text_lower = text.lower()
        score = 0.0
        
        # Check for uncertainty phrases
        uncertainty_count = sum(1 for phrase in self.uncertainty_phrases if phrase in text_lower)
        if uncertainty_count > 0:
            score += min(0.3 * uncertainty_count, 0.6)
        
        # Check response length (very short or very long can indicate issues)
        word_count = len(text.split())
        if word_count < 10:
            score += 0.3
        elif word_count > 500:
            score += 0.2
        
        # Check for repetition (simple heuristic)
        words = text_lower.split()
        if len(words) > 5:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:  # High repetition
                score += 0.4
        
        return min(score, 1.0)
    
    def _detect_toxicity(self, text: str) -> float:
        """
        Detect toxic or harmful language using regex patterns.
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        toxic_matches = 0
        
        for pattern in self.toxic_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            toxic_matches += len(matches)
        
        # Normalize score (cap at 5 matches = 1.0 score)
        toxicity_score = min(toxic_matches / 5.0, 1.0)
        
        return toxicity_score
    
    def _detect_safety_violations(self, prompt: str, response: str) -> float:
        """
        Detect safety violations or harmful intent in prompt/response.
        """
        combined_text = (prompt + ' ' + response).lower()
        
        violation_count = sum(
            1 for keyword in self.unsafe_keywords 
            if keyword in combined_text
        )
        
        # Normalize score (cap at 3 violations = 1.0 score)
        safety_score = min(violation_count / 3.0, 1.0)
        
        return safety_score
