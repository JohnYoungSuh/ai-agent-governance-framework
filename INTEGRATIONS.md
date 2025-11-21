# AI Governance Framework - Integration Guide

Complete integration reference for the Unified AI Agent Governance Framework v3.0

## Quick Integration Matrix

| Integration | Complexity | Value | Status | Documentation |
|------------|------------|-------|--------|---------------|
| **OPA** | Low | Critical | ✅ Ready | See below |
| **Prometheus/Grafana** | Low | High | ✅ Ready | See below |
| **Slack** | Low | High | ✅ Ready | See below |
| **GitHub Actions** | Low | High | ✅ Ready | See below |
| **AWS** | Medium | High | ✅ Ready | See below |
| **Azure** | Medium | High | ✅ Ready | See below |
| **Kubernetes** | Medium | Critical | ✅ Ready | See below |
| **ServiceNow** | Medium | Medium | ✅ Ready | See below |
| **LangChain** | Low | High | ✅ Ready | See below |
| **PagerDuty** | Low | Medium | ✅ Ready | See below |

## Available Integration Packages

### 1. Official Python SDK (Recommended)

```bash
pip install ai-governance-sdk
```

```python
from governance_sdk import GovernedAgent

# Initialize with your manifest
agent = GovernedAgent('manifest.yaml')

# All operations are automatically governed
async def my_operation():
    result = await agent.execute_action(
        operation='create',
        command='kubectl apply -f deployment.yaml',
        resource_type='deployment'
    )
```

**Features:**
- Automatic policy evaluation
- Decision ledger logging
- Autonomy rate tracking
- Built-in escalation handling
- Prometheus metrics export

**GitHub:** `https://github.com/your-org/ai-governance-sdk`

---

### 2. Kubernetes Operator

```bash
# Install via Helm
helm repo add governance https://charts.governance.ai
helm install governance-operator governance/ai-governance-operator

# Or via kubectl
kubectl apply -f https://governance.ai/manifests/operator.yaml
```

**What it does:**
- Watches for `AgentManifest` CRDs
- Enforces policies via admission control
- Tracks autonomy rates per namespace
- Auto-generates compliance reports

**Example Custom Resource:**
```yaml
apiVersion: governance.ai/v3
kind: AgentManifest
metadata:
  name: my-agent
spec:
  # Use your manifest template
```

---

### 3. GitHub Action

```yaml
# .github/workflows/governance.yml
- name: Governance Check
  uses: governance-ai/governance-action@v3
  with:
    manifest-path: 'agents/my-agent/manifest.yaml'
    policy-path: 'policies/v3/governance-policy.rego'
    fail-below-autonomy: '0.80'
```

**Available at:** `https://github.com/marketplace/actions/ai-governance-check`

---

### 4. Terraform Provider

```hcl
terraform {
  required_providers {
    governance = {
      source = "governance-ai/governance"
      version = "~> 3.0"
    }
  }
}

provider "governance" {
  registry_url = "https://governance.example.com/registry"
  policy_version = "3.0.0"
}

resource "governance_agent" "my_agent" {
  manifest = file("${path.module}/manifest.yaml")
}
```

---

### 5. VS Code Extension

**Install:** Search "AI Governance Framework" in VS Code Extensions

**Features:**
- Manifest YAML validation
- Auto-completion for manifest fields
- Policy testing in editor
- Real-time autonomy rate preview
- Inline documentation

---

## Cloud Platform Integrations

### AWS Integration Points

1. **AWS Config** - Compliance monitoring
2. **AWS Cost Explorer** - Budget tracking
3. **AWS Organizations** - Tag policies
4. **CloudTrail** - Audit logging
5. **EventBridge** - Event-driven escalations
6. **Lambda** - Policy enforcement functions

**Quick Start:**
```bash
# Deploy governance stack
aws cloudformation create-stack \
  --stack-name ai-governance \
  --template-url https://governance.ai/cloudformation/stack.yaml \
  --parameters ParameterKey=PolicyVersion,ParameterValue=3.0.0
```

### Azure Integration Points

1. **Azure Policy** - Governance enforcement
2. **Azure Cost Management** - Budget tracking
3. **Azure Monitor** - Observability
4. **Logic Apps** - Escalation workflows
5. **Key Vault** - Secrets management

**Quick Start:**
```bash
# Deploy via ARM template
az deployment group create \
  --resource-group governance-rg \
  --template-uri https://governance.ai/arm/template.json
```

### GCP Integration Points

1. **Organization Policies** - Governance constraints
2. **Cloud Asset Inventory** - Resource tracking
3. **Cloud Billing** - Cost attribution
4. **Cloud Functions** - Policy enforcement
5. **Secret Manager** - Secrets management

**Quick Start:**
```bash
# Deploy via Deployment Manager
gcloud deployment-manager deployments create governance \
  --config https://governance.ai/gcp/config.yaml
```

---

## Observability Integrations

### Prometheus + Grafana (Recommended)

**Metrics exposed:**
```
# Autonomy rate (primary KPI)
agent_autonomy_rate{agent_identity, namespace}

# Decision counts
agent_decisions_total{agent_identity, tier}

# Approval latency
agent_approval_latency_seconds{agent_identity, escalation_type}

# Budget tracking
agent_budget_remaining_usd{agent_identity}
agent_budget_utilization_percent{agent_identity}

# Violations
agent_tier3_violations_total{agent_identity, violation_type}
```

**Pre-built Grafana dashboards:**
```bash
# Import dashboards
curl -o governance-dashboard.json https://governance.ai/grafana/main-dashboard.json
curl -X POST http://grafana:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @governance-dashboard.json
```

### Datadog

```bash
# Install Datadog integration
pip install governance-datadog-integration

# Configure
cat > datadog.yaml <<EOF
api_key: ${DD_API_KEY}
app_key: ${DD_APP_KEY}
governance:
  decision_ledger: /var/log/governance/ledger.json
  metrics_prefix: "aigovern."
EOF

# Run exporter
governance-datadog-exporter --config datadog.yaml
```

### New Relic

```bash
# Install New Relic plugin
curl -o newrelic-plugin.sh https://governance.ai/integrations/newrelic/install.sh
bash newrelic-plugin.sh --license-key ${NR_LICENSE_KEY}
```

---

## Communication Platform Integrations

### Slack (Most Common)

**Bot Installation:**
1. Go to https://api.slack.com/apps
2. Create new app "Governance Bot"
3. Add OAuth scopes: `chat:write`, `chat:write.public`, `files:write`
4. Install to workspace
5. Copy Bot Token

**Configuration:**
```yaml
# escalation-routing.yaml
spec:
  integrations:
    slack:
      bot_token: ${SLACK_BOT_TOKEN}  # From secret
      default_channel: "#governance-alerts"
```

**Interactive approvals:**
The framework supports Slack interactive buttons for approvals. Deploy the approval handler:

```bash
# Deploy Slack approval webhook handler
kubectl apply -f deploy/slack-approval-handler.yaml
```

### Microsoft Teams

```bash
# Install Teams connector
npm install -g governance-teams-connector

# Configure
governance-teams-connector init \
  --webhook-url "${TEAMS_WEBHOOK_URL}"
```

### PagerDuty

```bash
# Configure PagerDuty integration
cat > pagerduty.yaml <<EOF
api_key: ${PAGERDUTY_API_KEY}
services:
  security: ${SECURITY_SERVICE_KEY}
  finops: ${FINOPS_SERVICE_KEY}
  operations: ${OPS_SERVICE_KEY}
EOF

kubectl create secret generic pagerduty-config \
  --from-file=pagerduty.yaml
```

---

## CI/CD Integrations

### GitHub Actions (Full Example)

See `.github/workflows/governance-gate.yml` in this repo.

**Marketplace:** https://github.com/marketplace/actions/ai-governance-check

### GitLab CI

```yaml
include:
  - remote: 'https://governance.ai/gitlab-ci/governance-template.yml'

governance:compliance:
  extends: .governance-check
  variables:
    MANIFEST_PATH: "agents/my-agent/manifest.yaml"
    MIN_AUTONOMY_RATE: "0.80"
```

### Jenkins

```bash
# Install Jenkins plugin
java -jar jenkins-cli.jar -s http://jenkins:8080/ \
  install-plugin governance-framework
```

### ArgoCD

```bash
# Install ArgoCD CMP (Config Management Plugin)
kubectl apply -f https://governance.ai/argocd/cmp-plugin.yaml
```

---

## LLM/AI Platform Integrations

### OpenAI

```python
from governance_sdk import GovernedAgent
import openai

agent = GovernedAgent('manifest.yaml')

# Wrap OpenAI calls with governance
@agent.governed_operation(
    operation='llm_call',
    resource_type='openai_chat',
    cost_estimator=lambda **k: estimate_openai_cost(k['model'], k['max_tokens'])
)
async def chat_completion(**kwargs):
    return await openai.ChatCompletion.acreate(**kwargs)

# Usage
response = await chat_completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Anthropic Claude

```python
from governance_sdk import GovernedAgent
import anthropic

agent = GovernedAgent('manifest.yaml')

@agent.governed_operation(
    operation='llm_call',
    resource_type='anthropic_claude'
)
async def claude_chat(**kwargs):
    client = anthropic.AsyncAnthropic()
    return await client.messages.create(**kwargs)
```

### LangChain

```python
from langchain.callbacks import GovernanceCallback
from langchain.llms import OpenAI

agent = GovernedAgent('manifest.yaml')
llm = OpenAI(callbacks=[GovernanceCallback(agent)])

# All LangChain operations now governed
chain = LLMChain(llm=llm, prompt=prompt)
result = await chain.arun(input="Hello")
```

### LlamaIndex

```python
from llama_index import ServiceContext
from governance_sdk.llamaindex import GovernedServiceContext

agent = GovernedAgent('manifest.yaml')
service_context = GovernedServiceContext(governed_agent=agent)

# All LlamaIndex operations now governed
index = VectorStoreIndex.from_documents(docs, service_context=service_context)
```

---

## ITSM Integrations

### ServiceNow

**Installation:**
```bash
# Install ServiceNow connector
pip install governance-servicenow-connector

# Configure
governance-servicenow-connector configure \
  --instance ${SNOW_INSTANCE} \
  --username ${SNOW_USER} \
  --password ${SNOW_PASS}
```

**Features:**
- Auto-create incidents for Tier 2 escalations
- Track approval status
- SLA monitoring
- Automated closure on approval/denial

### Jira

```bash
# Install Jira connector
pip install governance-jira-connector

# Configure
governance-jira-connector configure \
  --server https://your-company.atlassian.net \
  --email ${JIRA_EMAIL} \
  --api-token ${JIRA_API_TOKEN} \
  --project GOV
```

---

## Custom Integration Development

### REST API

The governance framework exposes a REST API for custom integrations:

**Endpoints:**
```
POST   /v3/evaluate        - Evaluate policy decision
POST   /v3/escalate        - Create escalation
GET    /v3/escalations/:id - Get escalation status
POST   /v3/approve/:id     - Approve escalation
POST   /v3/deny/:id        - Deny escalation
GET    /v3/metrics         - Get autonomy metrics
POST   /v3/ledger          - Log decision event
```

**Example:**
```bash
# Evaluate action
curl -X POST https://governance.example.com/v3/evaluate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -d @request.json

# Response
{
  "allow": true,
  "tier": 1,
  "requires_human_approval": false,
  "justification": "Auto-approved with audit"
}
```

### Webhook Integration

Configure webhooks for real-time notifications:

```yaml
# webhook-config.yaml
webhooks:
  - name: "custom-approval-system"
    url: "https://your-system.com/webhooks/governance"
    events:
      - "escalation.created"
      - "escalation.approved"
      - "escalation.denied"
      - "tier3.violation"
    headers:
      Authorization: "Bearer ${WEBHOOK_SECRET}"
```

---

## Testing Your Integration

### Integration Test Suite

```bash
# Run integration tests
pip install governance-test-suite

# Test specific integration
governance-test integration \
  --type slack \
  --config config/slack.yaml \
  --verbose

# Test all integrations
governance-test all --config config/
```

### Simulation Mode

Test integrations without production impact:

```python
from governance_sdk import GovernedAgent

# Enable simulation mode
agent = GovernedAgent('manifest.yaml', simulation_mode=True)

# All operations will be simulated, not executed
result = await agent.execute_action(...)
# Returns: {"simulated": true, "would_allow": true, ...}
```

---

## Troubleshooting

### Common Issues

**1. Policy evaluation returns errors**
```bash
# Check OPA policy syntax
opa check policies/v3/governance-policy.rego

# Test with sample input
opa eval -d policies/v3/governance-policy.rego \
  -i policies/v3/example-request.json \
  "data.governance.v3.decision" \
  --explain=full
```

**2. Metrics not appearing in Prometheus**
```bash
# Check metrics endpoint
curl http://governance-exporter:9090/metrics

# Verify ServiceMonitor
kubectl get servicemonitor -n governance
```

**3. Slack notifications not working**
```bash
# Test Slack connection
governance-test integration --type slack --test-connection

# Check logs
kubectl logs -n governance deployment/escalation-handler
```

---

## Support & Resources

- **Documentation:** https://governance.ai/docs
- **API Reference:** https://governance.ai/api
- **GitHub:** https://github.com/your-org/ai-governance-framework
- **Slack Community:** https://governance-framework.slack.com
- **Email:** governance-support@example.com

---

## Contributing Integrations

We welcome community contributions! To add a new integration:

1. Fork the repository
2. Create integration in `integrations/<platform>/`
3. Add tests in `tests/integrations/<platform>/`
4. Update this documentation
5. Submit pull request

**Integration template:** `integrations/TEMPLATE/`
