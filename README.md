# RiskGuard SDK

A lightweight SDK for monitoring LLM/API reliability, behavioral, and data privacy risks in real-time.

## Overview

RiskGuard sits inside your application and wraps LLM API calls to compute local risk signals across three categories:

1. **Reliability Risk** - Latency, errors, uptime, service availability
2. **Behavioral Risk** - Hallucinations, toxicity, safety violations
3. **Data Privacy Risk** - PII detection, sensitive data scanning

### Key Features

✅ **100% Local Scanning** - All analysis happens in your environment  
✅ **Privacy-First** - Raw prompts and responses NEVER leave your infrastructure  
✅ **Lightweight** - Minimal overhead, non-blocking design  
✅ **Metadata Only** - Only aggregate risk scores are computed and stored  
✅ **Rolling Window** - Configurable sliding window for real-time monitoring  

## Installation

```bash
pip install requests
```

## Quick Start

```python
from RiskGuard import RiskGuard

# Initialize SDK
rg = RiskGuard(window_size=20, timeout=3)

# Wrap your LLM call
prompt = "What is the capital of France?"
response = "The capital of France is Paris."

result = rg.chat(
    prompt=prompt,
    response_text=response
)

# Access immediate risk signals
print(result['behavioral_metadata'])
print(result['privacy_metadata'])

# Get aggregate metrics across rolling window
all_risks = rg.compute_all_risks()
print(all_risks['overall_risk_score'])
```

## Running the Demo

```bash
python demo.py
```

The demo runs 8 test cases covering different risk scenarios and displays detailed risk metrics.

## Privacy Guarantees

🔒 **Raw content NEVER leaves your environment**  
🔒 **Only aggregate scores are computed**  
🔒 **No logging of prompts or responses**  
🔒 **All scanning is local**  
🔒 **Metadata only contains counts and scores**  

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
