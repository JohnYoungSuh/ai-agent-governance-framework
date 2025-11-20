# AI Agent Runtime Controls

## Overview

This directory contains **5 critical runtime controls** that monitor, secure, and maintain AI agent operations in production. These controls address operational gaps in agent behavior monitoring, security, reliability, and quality maintenance.

## Controls Implemented

### ✅ Control #1: Runtime Behavior Monitoring
**File**: `agent_behavior_monitor.py`

**Purpose**: Monitor agent behavior in real-time and trigger circuit breakers on anomalies

**Features**:
- Statistical anomaly detection (Z-score based)
- Request rate monitoring
- Token usage tracking
- Cost spike detection
- Unauthorized action/API endpoint detection
- Automatic circuit breakers

**Usage**:
```python
from runtime_controls.agent_behavior_monitor import AgentBehaviorMonitor, AgentBehaviorBaseline, AgentActivity

# Load baseline from config
baseline = AgentBehaviorBaseline(
    agent_id="security-agent",
    tier=3,
    avg_requests_per_hour=10.0,
    std_requests_per_hour=2.0,
    # ... (see frameworks/agent-behavior-baselines.yaml)
)

# Create monitor
monitor = AgentBehaviorMonitor(baseline)

# Monitor each activity
activity = AgentActivity(
    timestamp=datetime.now(),
    action="scan_vulnerabilities",
    api_endpoint="trivy.io/scan",
    tokens_used=500,
    cost=0.05,
    success=True
)

is_normal = monitor.monitor(activity)
# If anomaly detected, circuit breaker triggers
```

**Configuration**: `frameworks/agent-behavior-baselines.yaml`

---

### ✅ Control #2: Advanced Prompt Injection Defense
**File**: `prompt_injection_defense.py`

**Purpose**: Multi-layer prompt injection detection and prevention

**Detection Layers**:
1. Text normalization (Unicode, zero-width chars)
2. Base64 decoding and scanning
3. Homoglyph detection
4. Pattern matching (50+ injection patterns)
5. Token repetition detection
6. Entropy analysis
7. Structural marker detection

**Usage**:
```python
from runtime_controls.prompt_injection_defense import PromptInjectionDefense

defense = PromptInjectionDefense()

# Validate user input before sending to LLM
result = defense.validate(user_input)

if not result.is_safe:
    raise SecurityError(f"Input rejected: {result.violations}")
    # Log to SIEM
    # Block request
```

**Performance**: 5-10ms latency per request

---

### ✅ Control #3: Agent Rollback Mechanism
**File**: `agent_rollback_monitor.py`

**Purpose**: Monitor agent performance and trigger automatic rollback

**Rollback Triggers**:
- Error rate >10% (configurable)
- P99 latency >5s (configurable)
- Cost spike >3x baseline

**Usage**:
```bash
# Run as sidecar container or CronJob
python3 agent_rollback_monitor.py \
  --agent security-agent \
  --namespace ai-agents-prod \
  --prometheus-url http://prometheus:9090 \
  --error-threshold 0.10 \
  --latency-threshold 5000 \
  --auto-rollback
```

**Integration**: Requires Prometheus metrics and Kubernetes API access

---

### ✅ Control #4: Agent Communication Protocol
**File**: `agent_message_validator.py`

**Purpose**: Validate and authenticate agent-to-agent messages

**Features**:
- HMAC-SHA256 signature verification
- Message deduplication (replay attack prevention)
- Schema validation
- Timestamp validation

**Usage**:
```python
from runtime_controls.agent_message_validator import AgentMessageValidator

# Initialize validator with shared secret
validator = AgentMessageValidator("security-agent", shared_secret)

# Send message
message = validator.create_message(
    recipient_agent_id="it-ops-agent",
    message_type="task_request",
    payload={"task": "restart_service", "parameters": {"service": "nginx"}}
)

# Receive and validate message
is_valid, errors = validator.validate(incoming_message)
if not is_valid:
    raise ValueError(f"Invalid message: {errors}")
```

**Configuration**: `frameworks/agent-communication-protocol.yaml`

---

### ✅ Control #5: Model Drift Detection
**File**: `model_drift_detector.py`

**Purpose**: Detect model performance degradation over time

**Detection Methods**:
- Accuracy tracking (sliding window)
- Confidence calibration analysis
- Distribution shift detection

**Usage**:
```python
from runtime_controls.model_drift_detector import ModelDriftDetector

# Initialize detector
detector = ModelDriftDetector(
    agent_id="security-agent",
    baseline_accuracy=0.95,
    drift_threshold=0.05,
    window_size=100
)

# Record predictions with ground truth (from human review)
detector.record_prediction(
    prediction="vulnerability_found",
    ground_truth="vulnerability_found",  # From MI-007 human review
    confidence=0.92
)

# Check for drift periodically
report = detector.detect_drift()
if report.drift_detected:
    detector.trigger_retraining_alert(report)
```

**Configuration**: `frameworks/model-drift-config.yaml`

---

## Installation

### Prerequisites

- Python 3.9+
- Required packages:
  ```bash
  pip install requests pyyaml
  ```

### Setup

1. **Copy runtime controls to agent pods**:
   ```bash
   # Add to Dockerfile
   COPY scripts/runtime-controls/ /app/runtime-controls/
   ```

2. **Load configuration**:
   ```bash
   # Mount ConfigMaps
   kubectl create configmap agent-behavior-baselines \
     --from-file=frameworks/agent-behavior-baselines.yaml \
     -n ai-agents-prod
   ```

3. **Set up secrets** (for agent communication):
   ```bash
   # Generate shared secret
   SECRET=$(openssl rand -hex 32)
   
   kubectl create secret generic agent-communication-secrets \
     --from-literal=security-agent=$SECRET \
     --from-literal=it-ops-agent=$SECRET \
     -n ai-agents-prod
   ```

---

## Integration with Existing Framework

### 1. Behavior Monitoring Integration

Add to agent initialization:
```python
# Load baseline from ConfigMap
import yaml
with open('/config/agent-behavior-baselines.yaml') as f:
    config = yaml.safe_load(f)
    baseline_data = config['baselines'][agent_id]

# Create monitor
from runtime_controls.agent_behavior_monitor import AgentBehaviorMonitor
monitor = AgentBehaviorMonitor(baseline_data)

# Monitor each action
def execute_action(action, **kwargs):
    activity = AgentActivity(...)
    monitor.monitor(activity)
    
    # Check if circuit breaker active
    if monitor.circuit_breaker_active:
        raise CircuitBreakerError("Agent paused due to anomalous behavior")
    
    # Execute action
    result = perform_action(action, **kwargs)
    return result
```

### 2. Prompt Injection Defense Integration

Replace existing MI-002 filter:
```python
# OLD: Basic pattern matching
# if any(pattern in user_input for pattern in INJECTION_PATTERNS):
#     raise SecurityError("Injection detected")

# NEW: Multi-layer defense
from runtime_controls.prompt_injection_defense import PromptInjectionDefense

defense = PromptInjectionDefense()
result = defense.validate(user_input)

if not result.is_safe:
    # Log to SIEM
    logger.critical(f"Prompt injection blocked: {result.violations}")
    
    # Increment Prometheus metric
    prometheus_client.Counter('prompt_injection_blocked_total').inc()
    
    raise SecurityError(f"Input rejected: {result.violations[0]}")
```

### 3. Rollback Monitor Deployment

Deploy as sidecar container:
```yaml
# Add to security-agent-deployment.yaml
spec:
  template:
    spec:
      containers:
      - name: agent
        # ... existing agent container
      
      - name: rollback-monitor
        image: python:3.9-slim
        command:
          - python3
          - /app/runtime-controls/agent_rollback_monitor.py
          - --agent=security-agent
          - --namespace=ai-agents-prod
          - --prometheus-url=http://prometheus:9090
          - --auto-rollback
        env:
          - name: KUBECONFIG
            value: /var/run/secrets/kubernetes.io/serviceaccount
        volumeMounts:
          - name: runtime-controls
            mountPath: /app/runtime-controls
```

### 4. Agent Communication Integration

Add to agent message handling:
```python
from runtime_controls.agent_message_validator import AgentMessageValidator

# Initialize validator
validator = AgentMessageValidator(
    agent_id=os.environ['AGENT_ID'],
    shared_secret=os.environ['AGENT_COMMUNICATION_SECRET']
)

# Send message to another agent
def send_message_to_agent(recipient_id, message_type, payload):
    message = validator.create_message(
        recipient_agent_id=recipient_id,
        message_type=message_type,
        payload=payload
    )
    
    # Send via HTTP/gRPC/message queue
    send_to_agent(message)

# Receive message from another agent
def handle_incoming_message(raw_message):
    message = AgentMessage(**raw_message)
    
    is_valid, errors = validator.validate(message)
    if not is_valid:
        logger.error(f"Invalid message: {errors}")
        return
    
    # Process message
    process_message(message)
```

### 5. Model Drift Detection Integration

Add to human review workflow (MI-007):
```python
from runtime_controls.model_drift_detector import ModelDriftDetector

# Initialize detector
detector = ModelDriftDetector(
    agent_id=agent_id,
    baseline_accuracy=0.95,
    drift_threshold=0.05
)

# After each human review
def record_human_review(agent_prediction, human_verdict, confidence):
    detector.record_prediction(
        prediction=agent_prediction,
        ground_truth=human_verdict,
        confidence=confidence
    )
    
    # Check for drift hourly
    if should_check_drift():
        report = detector.detect_drift()
        if report.drift_detected:
            # Create Jira ticket
            create_jira_ticket(
                project="ML",
                summary=f"Model drift detected: {agent_id}",
                description=f"Accuracy dropped from {report.baseline_accuracy:.2%} to {report.current_accuracy:.2%}"
            )
```

---

## Testing

### Run Unit Tests

```bash
# Test behavior monitoring
python3 -m pytest scripts/runtime-controls/test_agent_behavior_monitor.py

# Test prompt injection defense
python3 scripts/runtime-controls/prompt_injection_defense.py

# Test message validation
python3 scripts/runtime-controls/agent_message_validator.py

# Test drift detection
python3 scripts/runtime-controls/model_drift_detector.py
```

### Integration Testing

See `tests/runtime-controls/` for integration test scenarios.

---

## Monitoring

### Prometheus Metrics

All controls emit Prometheus metrics:

```
# Behavior monitoring
agent_behavior_anomalies_total{agent_id, anomaly_type}
agent_circuit_breaker_triggers_total{agent_id, reason}

# Prompt injection defense
prompt_injection_blocked_total{agent_id, detection_layer}
prompt_injection_latency_seconds{agent_id}

# Rollback monitor
agent_rollbacks_total{agent_id, namespace, reason}
agent_rollback_latency_seconds{agent_id}

# Agent communication
agent_messages_sent_total{sender, recipient, message_type}
agent_message_validation_failures_total{sender, recipient, failure_reason}

# Model drift
agent_model_drift_detected_total{agent_id}
agent_model_accuracy{agent_id}
```

### SIEM Events

All controls emit JSON events to stderr for SIEM ingestion:

```json
{
  "event_type": "agent_circuit_breaker_triggered",
  "agent_id": "security-agent",
  "reason": "Request rate 15x above baseline",
  "severity": "high",
  "timestamp": "2025-11-20T15:45:00Z"
}
```

---

## Troubleshooting

### Circuit Breaker False Positives

If circuit breakers trigger too frequently:

1. Check baseline accuracy:
   ```bash
   # Review actual agent behavior
   kubectl logs -n ai-agents-prod security-agent | grep "activity"
   ```

2. Adjust thresholds in `frameworks/agent-behavior-baselines.yaml`:
   ```yaml
   circuit_breaker:
     request_rate_threshold: 10.0  # Increase from 5.0
   ```

3. Switch to alert-only mode:
   ```yaml
   circuit_breaker:
     mode: alert_only  # Don't auto-pause
   ```

### Prompt Injection Defense Blocking Legitimate Input

If legitimate inputs are blocked:

1. Review violations:
   ```python
   result = defense.validate(user_input)
   print(result.violations)  # See which layer triggered
   ```

2. Adjust detection sensitivity (edit `prompt_injection_defense.py`):
   ```python
   self.max_input_length = 20000  # Increase from 10000
   ```

3. Add exemptions for specific patterns

### Rollback Monitor Not Triggering

1. Verify Prometheus connectivity:
   ```bash
   curl http://prometheus:9090/api/v1/query?query=up
   ```

2. Check metrics exist:
   ```bash
   curl "http://prometheus:9090/api/v1/query?query=agent_requests_total"
   ```

3. Lower thresholds for testing:
   ```bash
   python3 agent_rollback_monitor.py --error-threshold 0.05  # 5% instead of 10%
   ```

---

## Performance Impact

| Control | Latency | Memory | CPU |
|---------|---------|--------|-----|
| Behavior Monitoring | <1ms (async) | +50MB | +0.1 core |
| Prompt Injection Defense | 5-10ms (sync) | +30MB | +0.05 core |
| Rollback Monitor | N/A (background) | +20MB | +0.05 core |
| Message Validation | <2ms (sync) | +10MB | +0.02 core |
| Drift Detection | <1ms (async) | +30MB | +0.03 core |
| **Total** | **~10ms** | **+140MB** | **+0.25 core** |

---

## Next Steps

1. ✅ Deploy runtime controls to dev environment
2. ⏳ Tune baselines based on actual agent behavior (1-2 weeks)
3. ⏳ Enable circuit breakers in alert-only mode
4. ⏳ Monitor for false positives
5. ⏳ Switch to auto-pause mode in production
6. ⏳ Integrate with existing SIEM and alerting

---

## Resources

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [Prompt Injection Attacks](https://simonwillison.net/2023/Apr/14/worst-that-can-happen/)
- [Model Drift Detection](https://www.evidentlyai.com/blog/ml-monitoring-drift-detection)
