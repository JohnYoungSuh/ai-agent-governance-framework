# OpenTelemetry SIEM Integration

**AI Agent Governance Framework v2.1**
**Controls: AU-002, AU-012, G-03, SEC-001**

## Overview

This document describes the OpenTelemetry (OTel) integration for SIEM event emission in the AI Agent Governance Framework. The implementation conforms to the **Open Cybersecurity Schema Framework (OCSF)** for standardized security event reporting.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Compliance Checks & Audits                  │
│  (compliance-check-enhanced.sh, governance scripts, etc.)   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │  otel-siem-emitter.py     │
         │  - OCSF mapping           │
         │  - OTel spans & metrics   │
         │  - Fallback mode (JSON)   │
         └───────┬───────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
 ┌─────────┐         ┌──────────────┐
 │ OTLP    │         │ JSON Files   │
 │ Endpoint│         │ (fallback)   │
 └────┬────┘         └──────────────┘
      │
      ▼
┌──────────────────────────┐
│   SIEM Backends          │
│  - Splunk                │
│  - Datadog               │
│  - AWS CloudWatch        │
│  - Elastic Stack         │
│  - Custom collectors     │
└──────────────────────────┘
```

---

## Components

### 1. SIEM Event Emitter (`scripts/otel-siem-emitter.py`)

**Purpose:** Emit SIEM events via OpenTelemetry protocol with OCSF mapping.

**Key Features:**
- ✅ OCSF (Open Cybersecurity Schema Framework) compliant
- ✅ OpenTelemetry spans for distributed tracing
- ✅ Metrics (counters, gauges) for compliance tracking
- ✅ Fallback mode (works without OTel dependencies)
- ✅ Multiple SIEM backend support via OTLP

**Usage:**
```bash
python3 scripts/otel-siem-emitter.py \
    --agent-id security-agent \
    --control-id SEC-001 \
    --event-type compliance_check \
    --severity info \
    --description "KMS key rotation enabled" \
    --audit-id audit-12345 \
    --jira-cr-id CR-2025-1042 \
    --tier 3 \
    --compliance-result pass \
    --resource-arn "arn:aws:kms:us-east-1:123456789012:key/abc123"
```

**Event Types:**
- `compliance_check` - Compliance validation results
- `security_finding` - Security issues/violations
- `iam_change` - IAM role/policy changes
- `api_call` - API activity events
- `authentication` - Authentication/authorization events
- `resource_access` - Resource access events

**Severity Levels:**
- `info` (OCSF: 1) - Informational
- `low` (OCSF: 2) - Low severity
- `medium` (OCSF: 3) - Medium severity
- `high` (OCSF: 4) - High severity
- `critical` (OCSF: 5) - Critical severity

### 2. OCSF Mapping

The emitter automatically maps events to OCSF categories and classes:

| Event Type | OCSF Category | OCSF Class | Category UID | Class UID |
|-----------|---------------|------------|--------------|-----------|
| `compliance_check` | Findings | Compliance Finding | 2 | 2001 |
| `security_finding` | Findings | Detection Finding | 2 | 2004 |
| `iam_change` | IAM | Account Change | 3 | 3005 |
| `api_call` | Application | API Activity | 6 | 6003 |
| `authentication` | IAM | Authentication | 3 | 3001 |
| `resource_access` | Application | API Activity | 6 | 6003 |

**Example OCSF Output:**
```json
{
  "ocsf_mapping": {
    "category_uid": 2,
    "class_uid": 2001,
    "severity_id": 1,
    "activity_id": 1
  }
}
```

### 3. Schema Compliance (`policies/schemas/siem-event.json`)

All SIEM events conform to the JSON schema:

**Required Fields:**
- `siem_event_id` - Unique event identifier (correlates with `audit_id`)
- `timestamp` - ISO-8601 timestamp (UTC)
- `source` - Event source (`audit-trail`, `infra`, `jira`, etc.)
- `control_id` - Governance control ID (e.g., `SEC-001`)
- `agent_id` - Agent identifier
- `tier` - Agent tier (1-4)
- `ocsf_mapping` - OCSF category, class, severity

**Optional Fields:**
- `jira_reference` - Jira CR correlation (required for Tier 3/4)
- `payload` - Event-specific data
- `compliance_result` - `pass`, `fail`, `warning`
- `metadata` - Environment, correlation IDs, workflow IDs

---

## Setup

### 1. Install Dependencies

```bash
pip3 install -r scripts/requirements-otel.txt
```

**Dependencies:**
- `opentelemetry-api` - Core OTel API
- `opentelemetry-sdk` - OTel SDK
- `opentelemetry-exporter-otlp-proto-http` - HTTP OTLP exporter
- `opentelemetry-exporter-otlp-proto-grpc` - gRPC OTLP exporter (optional)

### 2. Configure Environment Variables

```bash
# OTLP endpoint (default: http://localhost:4318)
export OTEL_EXPORTER_OTLP_ENDPOINT="https://your-otlp-collector:4318"

# Authentication headers (if required)
export OTEL_EXPORTER_OTLP_HEADERS="x-api-key=your-api-key,x-tenant-id=your-tenant"

# Service identification
export OTEL_SERVICE_NAME="ai-agent-governance"
export OTEL_ENVIRONMENT="prod"  # dev, staging, prod
```

### 3. OTLP Collector Setup

**Option A: OpenTelemetry Collector**
```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:
    timeout: 10s
    send_batch_size: 1024

exporters:
  splunk_hec:
    endpoint: "https://splunk.example.com:8088/services/collector"
    token: "${SPLUNK_HEC_TOKEN}"
    source: "ai-agent-governance"
    sourcetype: "otel:siem"

  datadog:
    api:
      key: "${DATADOG_API_KEY}"

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [splunk_hec, datadog]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [splunk_hec, datadog]
```

**Option B: AWS CloudWatch**
```yaml
exporters:
  awscloudwatch:
    namespace: "AIAgentGovernance"
    region: "us-east-1"
    log_group_name: "/aws/ai-agents/siem"
    log_stream_name: "compliance-events"
```

**Option C: Direct Splunk HEC**
```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://splunk-hec.example.com:8088"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Splunk YOUR_HEC_TOKEN"
```

---

## Integration with Compliance Checks

### Example: KMS Key Rotation Check

```bash
#!/bin/bash
# From compliance-check-enhanced.sh

KMS_KEY_ID="arn:aws:kms:us-east-1:123456789012:key/abc123"

# Check KMS key rotation
ROTATION_ENABLED=$(aws kms get-key-rotation-status \
    --key-id "$KMS_KEY_ID" \
    --query 'KeyRotationEnabled' \
    --output text)

if [ "$ROTATION_ENABLED" = "True" ]; then
    RESULT="pass"
    SEVERITY="info"
    DESCRIPTION="KMS key rotation enabled"
else
    RESULT="fail"
    SEVERITY="high"
    DESCRIPTION="KMS key rotation DISABLED - violates SC-028"
fi

# Emit SIEM event
python3 scripts/otel-siem-emitter.py \
    --agent-id "${AGENT_NAME}" \
    --control-id "SEC-001" \
    --event-type "compliance_check" \
    --severity "$SEVERITY" \
    --description "$DESCRIPTION" \
    --audit-id "${AUDIT_ID}" \
    --jira-cr-id "${JIRA_CR_ID}" \
    --tier 3 \
    --compliance-result "$RESULT" \
    --resource-arn "$KMS_KEY_ID"
```

### Example: IAM Policy Change Detection

```bash
#!/bin/bash

IAM_ROLE="ai-agent-tier3-role"

# Detect wildcard permissions
POLICY_JSON=$(aws iam get-role-policy --role-name "$IAM_ROLE" --policy-name "AgentPolicy")

if echo "$POLICY_JSON" | grep -q '"Resource":\s*"\*"'; then
    # Emit security finding
    python3 scripts/otel-siem-emitter.py \
        --agent-id "security-monitor" \
        --control-id "SEC-001" \
        --event-type "security_finding" \
        --severity "critical" \
        --description "IAM role has wildcard resource permissions" \
        --audit-id "audit-$(date +%s)" \
        --tier 3 \
        --compliance-result "fail" \
        --resource-arn "arn:aws:iam::123456789012:role/$IAM_ROLE" \
        --payload-json "{\"policy_violations\":[\"wildcard_resource\"]}"
fi
```

---

## Fallback Mode (No OpenTelemetry)

If OpenTelemetry is not installed, the emitter runs in **fallback mode**:

- ✅ Generates SIEM event JSON (conforming to schema)
- ✅ Writes to `--output` file
- ✅ Prints JSON to stdout for logging
- ❌ No OTLP transmission
- ❌ No distributed tracing spans
- ❌ No metrics

**Fallback Workflow:**
```bash
# Without OTel installed
python3 scripts/otel-siem-emitter.py \
    --agent-id test-agent \
    --control-id SEC-001 \
    --event-type compliance_check \
    --severity info \
    --description "Test event" \
    --output /var/log/siem-events/event.json \
    --dry-run

# Output: JSON file written, no OTLP transmission
```

**Use Cases:**
- Development/testing without SIEM infrastructure
- Airgapped environments (JSON files shipped offline)
- Gradual migration to OTel

---

## Testing

### Run Test Suite

```bash
cd /home/suhlabs/projects/ai-agent-governance-framework
./scripts/test-siem-emitter.sh
```

**Test Coverage:**
- ✅ 10 test scenarios (6 positive, 4 negative)
- ✅ All event types
- ✅ All severity levels
- ✅ Jira CR correlation
- ✅ JSON schema validation
- ✅ OCSF mapping validation

**Example Output:**
```
==========================================
OpenTelemetry SIEM Emitter Test Suite
AI Agent Governance Framework v2.1
==========================================

Testing: Basic compliance check event (dry-run) ... ✅ PASS
Testing: Security finding (high severity) ... ✅ PASS
Testing: Invalid event type (negative test) ... ✅ PASS (expected failure)

==========================================
Test Summary
==========================================
Total Tests: 10
Passed: 10
Failed: 0

✅ All tests passed!
```

### Manual Testing

```bash
# Test with dry-run
python3 scripts/otel-siem-emitter.py \
    --agent-id test-agent \
    --control-id SEC-001 \
    --event-type compliance_check \
    --severity info \
    --description "Manual test" \
    --dry-run

# Test with output file
python3 scripts/otel-siem-emitter.py \
    --agent-id test-agent \
    --control-id SEC-001 \
    --event-type compliance_check \
    --severity info \
    --description "Manual test" \
    --output /tmp/test-event.json

# Validate JSON
python3 -c "import json; print(json.dumps(json.load(open('/tmp/test-event.json')), indent=2))"
```

---

## Metrics

The emitter automatically creates OpenTelemetry metrics:

### Counters

**`siem_events_total`** - Total SIEM events emitted
- Labels: `control_id`, `event_type`, `severity`, `compliance_result`

```promql
# Prometheus query examples
sum(siem_events_total) by (control_id)
rate(siem_events_total{compliance_result="fail"}[5m])
```

### Gauges

**`compliance_status`** - Compliance check results (+1 = pass, -1 = fail)
- Labels: `control_id`

```promql
# Compliance score by control
sum(compliance_status) by (control_id)
```

---

## Distributed Tracing

Each SIEM event creates an OpenTelemetry **span** with attributes:

```
Span: siem.compliance_check
  Attributes:
    - siem.event_id: audit-12345
    - siem.control_id: SEC-001
    - siem.agent_id: security-agent
    - siem.tier: 3
    - siem.severity: info
    - siem.compliance_result: pass
    - ocsf.category_uid: 2
    - ocsf.class_uid: 2001
    - ocsf.severity_id: 1
    - resource.arn: arn:aws:kms:...
    - jira.cr_id: CR-2025-1042
```

**Trace Context Propagation:**
- Audit ID serves as correlation ID
- Jira CR ID links to approval workflow
- Resource ARN enables resource-level tracing

---

## Troubleshooting

### Issue: "OpenTelemetry not installed"

**Symptom:**
```
⚠️  OpenTelemetry not installed - running in fallback mode (JSON-only)
```

**Solution:**
```bash
pip3 install -r scripts/requirements-otel.txt
```

### Issue: "Connection refused to OTLP endpoint"

**Symptom:**
```
ERROR: Failed to emit SIEM event: Connection refused
```

**Solution:**
1. Check OTLP collector is running:
   ```bash
   curl http://localhost:4318/v1/traces
   ```

2. Verify endpoint configuration:
   ```bash
   echo $OTEL_EXPORTER_OTLP_ENDPOINT
   ```

3. Test with dry-run mode:
   ```bash
   python3 scripts/otel-siem-emitter.py ... --dry-run
   ```

### Issue: "Invalid OCSF category/severity"

**Symptom:**
```
Invalid OCSF category_uid: 0 ❌
```

**Solution:**
- Verify event type is valid (see Event Types section)
- Check severity is in: `info`, `low`, `medium`, `high`, `critical`

---

## Security Considerations

### 1. Authentication

Always use authenticated OTLP endpoints in production:

```bash
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer YOUR_TOKEN"
```

### 2. TLS/SSL

Use HTTPS for OTLP transmission:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-collector.example.com:4318"
```

### 3. Data Minimization

Avoid including sensitive data in event descriptions:

```bash
# ❌ Bad
--description "User password: abc123 failed validation"

# ✅ Good
--description "User authentication failed - invalid credentials"
```

### 4. Audit Trail Correlation

Always include `audit_id` and `jira_cr_id` for Tier 3/4 events:

```bash
--audit-id "audit-$(date +%s)-$(uuidgen | cut -d'-' -f1)" \
--jira-cr-id "CR-2025-1042"
```

---

## References

### OpenTelemetry
- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [OTLP Protocol](https://opentelemetry.io/docs/specs/otlp/)
- [Python SDK](https://opentelemetry-python.readthedocs.io/)

### OCSF (Open Cybersecurity Schema Framework)
- [OCSF Documentation](https://schema.ocsf.io/)
- [Event Classes](https://schema.ocsf.io/1.0.0/classes)
- [Category UIDs](https://schema.ocsf.io/1.0.0/categories)

### Compliance Controls
- **AU-002** - Audit Events (NIST 800-53)
- **AU-012** - Audit Record Generation (NIST 800-53)
- **G-03** - Control Implementation Validation
- **SEC-001** - Security Configuration Compliance

---

**Version:** 2.1
**Last Updated:** 2025-10-18
**Control Coverage:** AU-002, AU-012, G-03, SEC-001
