# privacy_scanner.py
"""
Data privacy scanner for detecting PII and sensitive data.
All scanning happens locally - raw data never leaves the environment.
"""

import re
from typing import Dict, Any, List


class PrivacyScanner:
    """
    Local privacy scanner for detecting PII and sensitive data in prompts/responses.
    Uses regex patterns and keyword matching.
    """
    
    def __init__(self):
        # PII regex patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'zip_code': r'\b\d{5}(?:-\d{4})?\b',
        }
        
        # Sensitive data keywords
        self.sensitive_categories = {
            'health': [
                'medical', 'diagnosis', 'prescription', 'patient', 'hospital',
                'disease', 'medication', 'doctor', 'healthcare', 'symptoms'
            ],
            'financial': [
                'salary', 'income', 'account number', 'routing number', 'bank',
                'credit score', 'loan', 'mortgage', 'investment', 'portfolio'
            ],
            'legal': [
                'lawsuit', 'conviction', 'arrest', 'criminal record', 'attorney',
                'settlement', 'litigation', 'defendant', 'plaintiff'
            ],
            'personal': [
                'passport', 'driver license', 'birth certificate', 'maiden name',
                'security question', 'password', 'pin', 'mother\'s maiden name'
            ]
        }
        
    def scan(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Scan prompt and response for privacy risks.
        
        Args:
            prompt: User input prompt
            response: LLM response text
            
        Returns:
            Dictionary with privacy risk metadata (no raw content)
        """
        combined_text = prompt + ' ' + response
        
        # Detect PII
        pii_detections = self._detect_pii(combined_text)
        pii_count = sum(pii_detections.values())
        
        # Detect sensitive data
        sensitive_detections = self._detect_sensitive_data(combined_text)
        sensitive_term_count = sum(sensitive_detections.values())
        
        # Calculate privacy risk score
        privacy_risk = self._calculate_privacy_risk(pii_count, sensitive_term_count)
        
        return {
            'pii_detected': pii_count > 0,
            'pii_count': pii_count,
            'pii_types': [k for k, v in pii_detections.items() if v > 0],
            'sensitive_terms_detected': sensitive_term_count > 0,
            'sensitive_term_count': sensitive_term_count,
            'sensitive_categories': [k for k, v in sensitive_detections.items() if v > 0],
            'privacy_risk': round(privacy_risk, 3),
            'has_privacy_issues': privacy_risk > 0.5
        }
    
    def _detect_pii(self, text: str) -> Dict[str, int]:
        """
        Detect PII using regex patterns.
        Returns count of each PII type found.
        """
        detections = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            detections[pii_type] = len(matches)
        
        return detections
    
    def _detect_sensitive_data(self, text: str) -> Dict[str, int]:
        """
        Detect sensitive data categories using keyword matching.
        Returns count of matches per category.
        """
        text_lower = text.lower()
        detections = {}
        
        for category, keywords in self.sensitive_categories.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            detections[category] = count
        
        return detections
    
    def _calculate_privacy_risk(self, pii_count: int, sensitive_count: int) -> float:
        """
        Calculate overall privacy risk score (0-1).
        Weighted combination of PII and sensitive data.
        """
        # PII is more critical than sensitive keywords
        pii_score = min(pii_count / 3.0, 1.0)  # Cap at 3 PII items
        sensitive_score = min(sensitive_count / 5.0, 1.0)  # Cap at 5 sensitive terms
        
        privacy_risk = 0.7 * pii_score + 0.3 * sensitive_score
        
        return min(privacy_risk, 1.0)
