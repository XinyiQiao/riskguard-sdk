# riskguard.py
import time
from collections import deque
from statistics import mean
from reliability_scanner import ReliabilityScanner
from behavioral_scanner import BehavioralScanner
from privacy_scanner import PrivacyScanner

class RiskGuard:
    """
    RiskGuard SDK - Comprehensive LLM/API risk monitoring.
    
    Tracks three categories of risk:
    1. Reliability risk - latency, errors, uptime
    2. Behavioral risk - hallucinations, toxicity, safety violations
    3. Data privacy risk - PII, sensitive data detection
    
    All scanning happens locally. Only aggregate metadata is collected.
    """

    def __init__(self, window_size=20, timeout=3):
        self.window_size = window_size
        self.timeout = timeout
        
        # Rolling history buffers for behavioral risk
        self.hallucination_scores = deque(maxlen=window_size)
        self.toxicity_scores = deque(maxlen=window_size)
        self.safety_violation_scores = deque(maxlen=window_size)
        
        # Rolling history buffers for privacy risk
        self.pii_detections = deque(maxlen=window_size)
        self.sensitive_term_counts = deque(maxlen=window_size)
        self.privacy_risks = deque(maxlen=window_size)
        
        # Initialize scanners (modular design)
        self.reliability_scanner = ReliabilityScanner(window_size=window_size, timeout=timeout)
        self.behavioral_scanner = BehavioralScanner()
        self.privacy_scanner = PrivacyScanner()

    def chat(self, prompt, url=None, response_text=None):
        """
        Wraps an LLM/API call and computes all risk signals.
        
        Args:
            prompt: User input prompt (required for scanning)
            url: API endpoint (optional, for actual API calls)
            response_text: Pre-computed response (optional, for testing without API call)
        
        Returns:
            Dictionary with status, latency, error info, and risk metadata
        """
        response_body = response_text
        status_code = 200
        had_error = False
        latency = 0

        # Make actual API call if URL provided (uses reliability scanner)
        if url:
            api_result = self.reliability_scanner.make_api_call(url)
            status_code = api_result['status']
            response_body = api_result['body']
            had_error = api_result['error']
            latency = api_result['latency']
        else:
            # No API call - just scanning provided text
            # Reliability metrics won't be meaningful in this mode
            pass
        
        # Perform behavioral scanning (local, non-blocking)
        behavioral_metadata = {}
        if response_body:
            behavioral_metadata = self.behavioral_scanner.scan(prompt, response_body)
            self.hallucination_scores.append(behavioral_metadata['hallucination_score'])
            self.toxicity_scores.append(behavioral_metadata['toxicity_score'])
            self.safety_violation_scores.append(behavioral_metadata['safety_violation_score'])
        
        # Perform privacy scanning (local, non-blocking)
        privacy_metadata = {}
        if response_body:
            privacy_metadata = self.privacy_scanner.scan(prompt, response_body)
            self.pii_detections.append(1 if privacy_metadata['pii_detected'] else 0)
            self.sensitive_term_counts.append(privacy_metadata['sensitive_term_count'])
            self.privacy_risks.append(privacy_metadata['privacy_risk'])
        
        # Return result (DO NOT include raw prompt or response)
        return {
            "status": status_code,
            "latency": latency,
            "error": had_error,
            "body": response_body[:120] if response_body else None,  # truncated preview
            "behavioral_metadata": behavioral_metadata,
            "privacy_metadata": privacy_metadata
        }

    def compute_reliability_risk(self):
        """
        Compute reliability risk metadata using the reliability scanner.
        
        Returns:
            Dictionary with reliability metrics (delegated to ReliabilityScanner)
        """
        return self.reliability_scanner.compute_metrics()
    
    def compute_behavioral_risk(self):
        """
        Compute behavioral risk metadata from rolling window.
        
        Returns aggregate metrics (no raw content):
        - avg hallucination score
        - avg toxicity score
        - avg safety violation score
        - overall behavioral risk score
        - rate of behavioral issues
        """
        if not self.hallucination_scores:
            return {"behavioral_risk_score": None}
        
        avg_hallucination = mean(self.hallucination_scores)
        avg_toxicity = mean(self.toxicity_scores)
        avg_safety_violation = mean(self.safety_violation_scores)
        
        # Overall behavioral risk (weighted average)
        behavioral_risk = (
            0.4 * avg_hallucination +
            0.35 * avg_toxicity +
            0.25 * avg_safety_violation
        )
        
        # Rate of issues (any score > 0.5)
        issue_count = sum(
            1 for i in range(len(self.hallucination_scores))
            if (self.hallucination_scores[i] > 0.5 or 
                self.toxicity_scores[i] > 0.5 or 
                self.safety_violation_scores[i] > 0.5)
        )
        issue_rate = issue_count / len(self.hallucination_scores)
        
        return {
            "avg_hallucination_score": round(avg_hallucination, 3),
            "avg_toxicity_score": round(avg_toxicity, 3),
            "avg_safety_violation_score": round(avg_safety_violation, 3),
            "behavioral_risk_score": round(behavioral_risk, 3),
            "behavioral_issue_rate": round(issue_rate, 3),
            "behavioral_issue_count": issue_count
        }
    
    def compute_privacy_risk(self):
        """
        Compute privacy risk metadata from rolling window.
        
        Returns aggregate metrics (no raw PII):
        - PII detection rate
        - avg sensitive term count
        - overall privacy risk score
        - privacy violation count
        """
        if not self.privacy_risks:
            return {"privacy_risk_score": None}
        
        pii_detection_rate = sum(self.pii_detections) / len(self.pii_detections)
        avg_sensitive_terms = mean(self.sensitive_term_counts)
        avg_privacy_risk = mean(self.privacy_risks)
        
        # Count privacy violations (privacy_risk > 0.5)
        violation_count = sum(1 for risk in self.privacy_risks if risk > 0.5)
        violation_rate = violation_count / len(self.privacy_risks)
        
        return {
            "pii_detection_rate": round(pii_detection_rate, 3),
            "avg_sensitive_term_count": round(avg_sensitive_terms, 2),
            "privacy_risk_score": round(avg_privacy_risk, 3),
            "privacy_violation_rate": round(violation_rate, 3),
            "privacy_violation_count": violation_count
        }
    
    def compute_all_risks(self):
        """
        Compute comprehensive risk metadata across all categories.
        
        Returns:
            Dictionary with reliability, behavioral, and privacy metrics.
            Only aggregate metadata - no raw prompts or responses.
        """
        reliability = self.compute_reliability_risk()
        behavioral = self.compute_behavioral_risk()
        privacy = self.compute_privacy_risk()
        
        # Calculate overall risk score (equal weighting)
        overall_risk = None
        if (reliability.get('reliability_risk_score') is not None and
            behavioral.get('behavioral_risk_score') is not None and
            privacy.get('privacy_risk_score') is not None):
            
            overall_risk = (
                0.33 * reliability['reliability_risk_score'] +
                0.33 * behavioral['behavioral_risk_score'] +
                0.34 * privacy['privacy_risk_score']
            )
        
        return {
            "overall_risk_score": round(overall_risk, 3) if overall_risk else None,
            "reliability": reliability,
            "behavioral": behavioral,
            "privacy": privacy,
            "request_volume": reliability.get('request_volume', 0)
        }