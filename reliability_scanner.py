# reliability_scanner.py
"""
Reliability scanner for tracking API/LLM performance metrics.
Monitors latency, errors, uptime, and service availability.
"""

import time
import requests
from collections import deque
from statistics import mean
from typing import Dict, Any, Optional


class ReliabilityScanner:
    """
    Tracks reliability metrics for LLM/API calls using a rolling window.
    Monitors latency, error rates, uptime, and incidents.
    """
    
    def __init__(self, window_size: int = 20, timeout: int = 3):
        """
        Initialize reliability scanner.
        
        Args:
            window_size: Number of requests to track in rolling window
            timeout: Request timeout in seconds
        """
        self.window_size = window_size
        self.timeout = timeout
        
        # Rolling history buffers
        self.latencies = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        self.successes = deque(maxlen=window_size)
    
    def make_api_call(self, url: str) -> Dict[str, Any]:
        """
        Make an API call and track reliability metrics.
        
        Args:
            url: API endpoint to call
            
        Returns:
            Dictionary with response details and reliability metadata
        """
        start = time.perf_counter()
        
        try:
            response = requests.get(url, timeout=self.timeout)
            latency = time.perf_counter() - start
            
            status_code = response.status_code
            response_body = response.text
            had_error = response.status_code >= 400
            
            # Track metrics
            self.latencies.append(latency)
            self.successes.append(1 if response.status_code == 200 else 0)
            self.errors.append(1 if response.status_code >= 400 else 0)
            
            return {
                "status": status_code,
                "latency": latency,
                "error": had_error,
                "body": response_body,
                "exception": None
            }
            
        except Exception as e:
            latency = time.perf_counter() - start
            
            # Track failure metrics
            self.latencies.append(latency)
            self.successes.append(0)
            self.errors.append(1)
            
            return {
                "status": "exception",
                "latency": latency,
                "error": True,
                "body": str(e),
                "exception": type(e).__name__
            }
    
    def compute_metrics(self) -> Dict[str, Any]:
        """
        Compute reliability metrics from rolling window.
        
        Returns:
            Dictionary with reliability risk scores and metadata
        """
        if not self.latencies:
            return {
                "reliability_risk_score": None,
                "avg_latency": None,
                "error_rate": None,
                "success_rate": None,
                "uptime": None,
                "incident_count": None,
                "request_volume": 0,
                "reliability_score": None
            }
        
        avg_latency = mean(self.latencies)
        error_rate = sum(self.errors) / len(self.errors)
        success_rate = sum(self.successes) / len(self.successes)
        request_volume = len(self.latencies)
        uptime = success_rate
        
        # Count incidents (API down events)
        incident_count = sum(1 for e in self.errors if e == 1)
        
        # Heuristic risk score
        risk_score = (
            0.5 * error_rate +
            0.3 * min(avg_latency / 2.0, 1.0) +  # normalize latency, cap at 1.0
            0.2 * (1 - success_rate)
        )
        risk_score = min(risk_score, 1.0)
        reliability_score = 1 - risk_score
        
        return {
            "avg_latency": round(avg_latency, 4),
            "error_rate": round(error_rate, 3),
            "success_rate": round(success_rate, 3),
            "uptime": round(uptime, 3),
            "incident_count": incident_count,
            "request_volume": request_volume,
            "reliability_risk_score": round(risk_score, 3),
            "reliability_score": round(reliability_score, 3)
        }
