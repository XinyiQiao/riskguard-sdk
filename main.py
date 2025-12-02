# driver.py
from RiskGuard import RiskGuard
import time

# Initialize the SDK
rg = RiskGuard(window_size=20, timeout=2)

TEST_URL = "https://api.github.com"  # reliable API
# TEST_URL = "https://httpstat.us/500"  # simulate consistent error
# TEST_URL = "https://httpstat.us/200?sleep=2000"  # simulate slow API

print("Starting reliability test...\n")

for i in range(30):
    print(f"--- API CALL #{i+1} ---")
    result = rg.chat(TEST_URL)
    print("status:", result["status"])
    print("latency:", round(result["latency"], 4), "seconds")
    print("error:", result["error"])
    print()

    scores = rg.compute_reliability_risk()
    print("Rolling Metrics:", scores)
    print()

    time.sleep(0.5)  # avoid spamming too fast

print("\n=== Final Reliability Risk Score ===")
print(scores)