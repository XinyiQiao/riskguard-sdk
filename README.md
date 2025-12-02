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

## Architecture

```
┌─────────────────────────────────────────────┐
│           Your Application                  │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │        RiskGuard SDK                  │ │
│  │                                       │ │
│  │  ┌──────────────────────────────┐   │ │
│  │  │  Behavioral Scanner          │   │ │
│  │  │  - Hallucination detection   │   │ │
│  │  │  - Toxicity detection        │   │ │
│  │  │  - Safety violations         │   │ │
│  │  └──────────────────────────────┘   │ │
│  │                                       │ │
│  │  ┌──────────────────────────────┐   │ │
│  │  │  Privacy Scanner             │   │ │
│  │  │  - PII detection (regex)     │   │ │
│  │  │  - Sensitive data keywords   │   │ │
│  │  │  - Privacy risk scoring      │   │ │
│  │  └──────────────────────────────┘   │ │
│  │                                       │ │
│  │  ┌──────────────────────────────┐   │ │
│  │  │  Reliability Tracker         │   │ │
│  │  │  - Latency monitoring        │   │ │
│  │  │  - Error rate tracking       │   │ │
│  │  │  - Uptime calculation        │   │ │
│  │  └──────────────────────────────┘   │ │
│  └───────────────────────────────────────┘ │
│                                             │
│           ↓ (Metadata Only)                 │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │    Backend API (Optional)             │ │
│  │    - Aggregate risk scores            │ │
│  │    - No raw content                   │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

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

## API Reference

### `RiskGuard(window_size=20, timeout=3)`

Initialize the RiskGuard SDK.

**Parameters:**
- `window_size` (int): Number of requests to track in rolling window
- `timeout` (int): API timeout in seconds

### `chat(prompt, url=None, response_text=None)`

Wrap an LLM/API call and compute risk signals.

**Parameters:**
- `prompt` (str): User input prompt (required)
- `url` (str, optional): API endpoint for actual HTTP call
- `response_text` (str, optional): Pre-computed response for testing

**Returns:** Dictionary with:
- `status`: HTTP status code or "exception"
- `latency`: Request latency in seconds
- `error`: Boolean indicating error state
- `behavioral_metadata`: Behavioral risk scores
- `privacy_metadata`: Privacy risk scores

### `compute_reliability_risk()`

Get reliability metrics from rolling window.

**Returns:** Dictionary with:
- `avg_latency`: Average request latency
- `error_rate`: Percentage of failed requests
- `success_rate`: Percentage of successful requests
- `uptime`: Service uptime percentage
- `incident_count`: Number of failures
- `request_volume`: Total requests in window
- `reliability_risk_score`: 0-1 risk score

### `compute_behavioral_risk()`

Get behavioral risk metrics from rolling window.

**Returns:** Dictionary with:
- `avg_hallucination_score`: Average hallucination score
- `avg_toxicity_score`: Average toxicity score
- `avg_safety_violation_score`: Average safety violation score
- `behavioral_risk_score`: Overall 0-1 risk score
- `behavioral_issue_rate`: Percentage with issues
- `behavioral_issue_count`: Number of problematic responses

### `compute_privacy_risk()`

Get privacy risk metrics from rolling window.

**Returns:** Dictionary with:
- `pii_detection_rate`: Percentage with PII detected
- `avg_sensitive_term_count`: Average sensitive terms per request
- `privacy_risk_score`: Overall 0-1 risk score
- `privacy_violation_rate`: Percentage with violations
- `privacy_violation_count`: Number of privacy issues

### `compute_all_risks()`

Get comprehensive metrics across all risk categories.

**Returns:** Dictionary with:
- `overall_risk_score`: Combined risk score (0-1)
- `reliability`: Reliability metrics
- `behavioral`: Behavioral metrics
- `privacy`: Privacy metrics
- `request_volume`: Total requests tracked

## Risk Detection Methods

### Behavioral Scanning

**Hallucination Detection:**
- Uncertainty phrase detection ("I think", "maybe", "not sure")
- Response length anomalies (too short or too long)
- Repetition analysis (low unique word ratio)

**Toxicity Detection:**
- Regex pattern matching for offensive language
- Harmful content keywords

**Safety Violations:**
- Unsafe keyword detection (violence, illegal activities)
- Harmful intent patterns

### Privacy Scanning

**PII Detection (Regex):**
- Email addresses
- Phone numbers
- SSN
- Credit card numbers
- IP addresses
- ZIP codes

**Sensitive Data Detection (Keywords):**
- Health: medical, diagnosis, prescription, patient
- Financial: salary, account number, credit score
- Legal: lawsuit, criminal record, conviction
- Personal: passport, driver license, security questions

## Example Use Cases

### 1. Real-time Monitoring

```python
rg = RiskGuard(window_size=50)

for user_request in incoming_requests:
    result = rg.chat(
        prompt=user_request.prompt,
        url="https://api.openai.com/v1/chat/completions"
    )
    
    # Check immediate risks
    if result['behavioral_metadata']['has_behavioral_issues']:
        log_warning("Behavioral risk detected")
    
    if result['privacy_metadata']['has_privacy_issues']:
        log_alert("Privacy violation detected")
```

### 2. Periodic Risk Reporting

```python
rg = RiskGuard(window_size=100)

# Process requests...
# ...

# Every hour, report metrics
metrics = rg.compute_all_risks()
send_to_backend(metrics)  # Only metadata, no raw content
```

### 3. Testing & Validation

```python
# Test without making actual API calls
rg = RiskGuard()

result = rg.chat(
    prompt="Test prompt",
    response_text="Test response"
)

assert result['privacy_metadata']['pii_detected'] == False
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

## Limitations

- **Behavioral scanning** uses heuristic methods (not ML-based NLI)
- **PII detection** uses regex (may have false positives/negatives)
- **Performance** is optimized for speed over accuracy
- **Designed for English** text primarily

## Future Enhancements

- [ ] Integration with local transformer models (e.g., HuggingFace)
- [ ] Advanced NLI-based hallucination detection
- [ ] Microsoft Presidio integration for PII
- [ ] Async/non-blocking scanning option
- [ ] Multi-language support
- [ ] Custom rule configuration

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
