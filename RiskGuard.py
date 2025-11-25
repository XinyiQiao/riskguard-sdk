# riskguard.py
import time
import requests
from collections import deque
from statistics import mean

class RiskGuard:
    """
    RiskGuard SDK prototype.
    Tracks LLM/API reliability signals:
    - latency
    - HTTP error codes
    - timeouts
    - rolling reliability risk score
    """

    def __init__(self, window_size=20, timeout=3):
        self.window_size = window_size
        self.timeout = timeout

        # Rolling history buffers
        self.latencies = deque(maxlen=window_size)
        self.errors = deque(maxlen=window_size)
        self.successes = deque(maxlen=window_size)

    def call_api(self, url):
        """ Wraps an API call and computes reliability signals. """

        start = time.perf_counter()

        try:
            response = requests.get(url, timeout=self.timeout)
            latency = time.perf_counter() - start

            self.latencies.append(latency)
            self.successes.append(1 if response.status_code == 200 else 0)
            self.errors.append(1 if response.status_code >= 400 else 0)

            return {
                "status": response.status_code,
                "latency": latency,
                "error": response.status_code >= 400,
                "body": response.text[:120]  # truncated
            }

        except Exception as e:
            latency = time.perf_counter() - start

            self.latencies.append(latency)
            self.successes.append(0)
            self.errors.append(1)

            return {
                "status": "exception",
                "latency": latency,
                "error": True,
                "body": str(e)
            }

    def compute_reliability_risk(self):
        """ 
        Basic reliability risk model:
        - higher latency increases risk
        - higher error rate increases risk
        - lower success rate increases risk
        """

        if not self.latencies:
            return {"risk_score": None}

        avg_latency = mean(self.latencies)
        error_rate = sum(self.errors) / len(self.errors)
        success_rate = sum(self.successes) / len(self.successes)

        # Heuristic risk formula (you can refine this)
        risk_score = (
            0.5 * error_rate +
            0.3 * (avg_latency / 2.0) +  # normalize latency
            0.2 * (1 - success_rate)
        )

        return {
            "avg_latency": avg_latency,
            "error_rate": error_rate,
            "success_rate": success_rate,
            "risk_score": min(risk_score, 1.0)
        }