# Governance Framework v3.0 - Machine-Readable Policies

This directory contains machine-readable policy files that can be directly implemented in AI agent systems.

## Files Overview

### 1. `agent-manifest-template.yaml`
**Purpose:** Template for agent deployment manifests

**Usage:**
```bash
# Copy template for new agent
cp agent-manifest-template.yaml ../../agents/my-agent/manifest.yaml

# Fill in all <placeholders>
# Compute policy hash
sha256sum ../UNIFIED-AI-AGENT-GOVERNANCE-FRAMEWORK-v3.0.md

# Sign manifest
openssl dgst -sha256 -sign private-key.pem -out manifest.sig manifest.yaml
```

**Required fields:**
- All fields marked with `<...>` must be filled
- Cost center and project code must be valid
- Resource quotas must be realistic
- Budget must be approved

### 2. `action-tier-rules.json`
**Purpose:** Decision matrix for action tier classification

**Usage:**
```bash
# Validate JSON schema
jsonschema -i action-tier-rules.json schema.json

# Query specific rule
jq '.rules[] | select(.rule_id=="tier1-write-own-namespace")' action-tier-rules.json

# Test pattern matching (requires custom tool)
./test-pattern-match.sh "kubectl apply -f deploy.yaml -n team-alpha" action-tier-rules.json
```

**Integration:**
- Import into policy engine
- Use patterns for regex matching
- Evaluate conditions before approval
- Route escalations per approval_routing

### 3. `governance-policy.rego`
**Purpose:** Open Policy Agent (OPA) policy implementation

**Usage:**
```bash
# Test policy with example request
opa eval -d governance-policy.rego -i example-request.json "data.governance.v3.decision"

# Run policy server
opa run --server --addr :8181 governance-policy.rego

# Query via API
curl -X POST http://localhost:8181/v1/data/governance/v3/decision \
  -H 'Content-Type: application/json' \
  -d @example-request.json
```

**Output format:**
```json
{
  "allow": true,
  "tier": 1,
  "requires_human_approval": false,
  "approval_routing": null,
  "justification": "Auto-approved with audit: Write operation within quota and policy",
  "violations": [],
  "recommendations": [],
  "audit_level": "info",
  "simulation_required": false
}
```

**Integration with Kubernetes:**
```yaml
# Admission controller configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: opa-policy
  namespace: governance
data:
  governance-v3.rego: |
    <paste governance-policy.rego content>
```

### 4. `escalation-routing.yaml`
**Purpose:** Configuration for human escalation routing

**Usage:**
```bash
# Apply to Kubernetes cluster
kubectl apply -f escalation-routing.yaml

# Validate configuration
kubectl get escalationroutingconfig default-escalation-routing -o yaml

# Test routing logic (requires custom tool)
./test-escalation-routing.sh --trigger=budget_overage --agent=team-alpha-agent
```

**Integration:**
- Load into escalation service
- Configure Slack/PagerDuty webhooks
- Set up ServiceNow integration
- Configure SMTP for email

### 5. `example-request.json`
**Purpose:** Example policy request for testing

**Usage:**
```bash
# Test with OPA
opa eval -d governance-policy.rego -i example-request.json "data.governance.v3.decision"

# Modify for different scenarios
cp example-request.json test-tier2-budget.json
# Edit to set budget_remaining < 0

# Validate against schema
jsonschema -i example-request.json request-schema.json
```

## Quick Start: Testing the Policy

### 1. Install OPA
```bash
# macOS
brew install opa

# Linux
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa
sudo mv opa /usr/local/bin/
```

### 2. Test Policy Decision
```bash
# Tier 0 (auto-approve): Read operation
cat > test-tier0.json <<EOF
{
  "agent_identity": "team-alpha-agent-001",
  "namespace": "team-alpha",
  "operation": "get",
  "command": "kubectl get pods -n team-alpha",
  "policy_version": "3.0.0",
  "current_cpu_usage": 10,
  "declared_cpu_quota": 16,
  "current_memory_usage": 20,
  "declared_memory_quota": 32,
  "current_storage_usage": 40,
  "declared_storage_quota": 100,
  "budget_limit_usd": 500,
  "current_spending_usd": 300,
  "resource_tags": {
    "agent_identity": "team-alpha-agent-001",
    "cost_center": "CC-1234",
    "project_code": "PROJ-5678"
  }
}
EOF

opa eval -d governance-policy.rego -i test-tier0.json "data.governance.v3.decision"
```

### 3. Test Tier 2 Escalation
```bash
# Tier 2: Budget overage
cat > test-tier2-budget.json <<EOF
{
  "agent_identity": "team-alpha-agent-001",
  "namespace": "team-alpha",
  "operation": "create",
  "command": "kubectl apply -f expensive-deployment.yaml -n team-alpha",
  "policy_version": "3.0.0",
  "current_cpu_usage": 10,
  "declared_cpu_quota": 16,
  "current_memory_usage": 20,
  "declared_memory_quota": 32,
  "current_storage_usage": 40,
  "declared_storage_quota": 100,
  "budget_limit_usd": 500,
  "current_spending_usd": 520,
  "resource_tags": {
    "agent_identity": "team-alpha-agent-001",
    "cost_center": "CC-1234",
    "project_code": "PROJ-5678"
  }
}
EOF

opa eval -d governance-policy.rego -i test-tier2-budget.json "data.governance.v3.decision"
# Expected: requires_human_approval: true, approval_routing: ["finops_team", ...]
```

### 4. Test Tier 3 Denial
```bash
# Tier 3: Credential exposure attempt
cat > test-tier3.json <<EOF
{
  "agent_identity": "team-alpha-agent-001",
  "namespace": "team-alpha",
  "operation": "execute",
  "command": "echo $DATABASE_PASSWORD",
  "policy_version": "3.0.0",
  "resource_tags": {
    "agent_identity": "team-alpha-agent-001",
    "cost_center": "CC-1234",
    "project_code": "PROJ-5678"
  }
}
EOF

opa eval -d governance-policy.rego -i test-tier3.json "data.governance.v3.decision"
# Expected: allow: false, tier: 3, justification: "DENIED: Attempted credential exposure"
```

## Integration Examples

### Kubernetes Admission Controller
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: governance-admission-controller
  namespace: governance
spec:
  replicas: 3
  selector:
    matchLabels:
      app: governance-admission
  template:
    metadata:
      labels:
        app: governance-admission
    spec:
      containers:
      - name: opa
        image: openpolicyagent/opa:latest
        args:
          - "run"
          - "--server"
          - "--addr=:8181"
          - "/policies/governance-policy.rego"
        volumeMounts:
        - name: policies
          mountPath: /policies
      volumes:
      - name: policies
        configMap:
          name: opa-policies
```

### GitHub Actions CI/CD Gate
```yaml
name: Governance Compliance Check
on: [push, pull_request]

jobs:
  governance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Install OPA
        run: |
          curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
          chmod +x opa
          sudo mv opa /usr/local/bin/

      - name: Validate Agent Manifest
        run: |
          # Check manifest exists
          if [ ! -f agent-manifest.yaml ]; then
            echo "ERROR: agent-manifest.yaml not found"
            exit 1
          fi

          # Validate YAML syntax
          yamllint agent-manifest.yaml

          # Check required fields
          yq eval '.spec.compliance.framework_version' agent-manifest.yaml | grep -q "3.0.0"

      - name: Test Policy Compliance
        run: |
          # Generate test request from manifest
          ./scripts/generate-test-request.sh agent-manifest.yaml > test-request.json

          # Evaluate policy
          opa eval -d policies/v3/governance-policy.rego \
            -i test-request.json \
            "data.governance.v3.decision" \
            --format pretty

      - name: Check for Violations
        run: |
          VIOLATIONS=$(opa eval -d policies/v3/governance-policy.rego \
            -i test-request.json \
            "data.governance.v3.decision.violations" \
            --format raw)

          if [ "$VIOLATIONS" != "[]" ]; then
            echo "Policy violations detected:"
            echo "$VIOLATIONS"
            exit 1
          fi
```

### Terraform Policy Validation
```hcl
# sentinel.hcl
policy "governance_compliance" {
  source            = "./policies/v3/governance-policy.rego"
  enforcement_level = "hard-mandatory"
}

module "opa_policy" {
  source = "terraform-opa-policy-module"

  policy_file = "${path.module}/policies/v3/governance-policy.rego"
  test_cases  = "${path.module}/policies/v3/test-cases/"
}
```

## Monitoring & Observability

### Prometheus Metrics
```yaml
# ServiceMonitor for governance policy engine
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: governance-policy-metrics
spec:
  selector:
    matchLabels:
      app: governance-policy-engine
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

**Key metrics to track:**
- `governance_decisions_total{tier="0|1|2|3"}`
- `governance_approvals_pending{routing="finops|security|namespace_owner"}`
- `governance_approval_latency_seconds{tier="2"}`
- `governance_violations_total{severity="critical|high|medium|low"}`
- `governance_autonomy_rate{agent="<agent_identity>"}`

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "AI Agent Governance - Autonomy Metrics",
    "panels": [
      {
        "title": "Autonomy Rate by Agent",
        "targets": [
          {
            "expr": "sum(rate(governance_decisions_total{tier=~\"0|1\"}[7d])) by (agent) / sum(rate(governance_decisions_total[7d])) by (agent)"
          }
        ],
        "threshold": 0.80
      },
      {
        "title": "Pending Approvals",
        "targets": [
          {
            "expr": "governance_approvals_pending"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### Common Issues

**1. Policy version mismatch**
```bash
# Check agent's policy version
yq eval '.spec.compliance.framework_version' agent-manifest.yaml

# Should match framework version: 3.0.0
```

**2. Pattern not matching**
```bash
# Test regex pattern
echo "kubectl get pods -n team-alpha" | grep -E "^(get|list|describe) .* --namespace=team-alpha$"

# If no match, check action-tier-rules.json patterns
```

**3. OPA evaluation errors**
```bash
# Run with trace for debugging
opa eval -d governance-policy.rego -i test-request.json \
  "data.governance.v3.decision" \
  --explain=full
```

## Support

For questions or issues:
- Slack: `#ai-governance`
- Email: `governance-team@example.com`
- Documentation: `https://governance.example.com/docs/v3`
