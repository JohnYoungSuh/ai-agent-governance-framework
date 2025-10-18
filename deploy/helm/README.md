# Helm Charts for AI Agents

This directory contains Helm charts for deploying AI agents to Kubernetes.

## Chart Structure

```
helm/
└── ai-agent/                       # Universal AI agent chart
    ├── Chart.yaml                  # Chart metadata
    ├── values.yaml                 # Default values
    ├── values-security.yaml        # Security Agent values
    ├── values-itops.yaml           # IT-Ops Agent values
    ├── values-ai.yaml              # AI Agent values
    ├── values-architect.yaml       # Architect Agent values
    ├── templates/
    │   ├── _helpers.tpl            # Template helpers
    │   ├── deployment.yaml         # Deployment template
    │   ├── service.yaml            # Service template
    │   ├── configmap.yaml          # ConfigMap template
    │   ├── serviceaccount.yaml     # ServiceAccount template
    │   ├── hpa.yaml                # HorizontalPodAutoscaler template
    │   ├── pvc.yaml                # PersistentVolumeClaim template
    │   ├── networkpolicy.yaml      # NetworkPolicy template
    │   └── externalsecret.yaml     # ExternalSecret template
    └── README.md                   # This file
```

## Quick Start

### Install Security Agent

```bash
helm install security-agent ai-agent \
  --namespace ai-agents-prod \
  --create-namespace \
  --values ai-agent/values-security.yaml
```

### Install All Agents

```bash
# Security Agent (Tier 3)
helm install security-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-security.yaml

# IT-Ops Agent (Tier 3)
helm install it-ops-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-itops.yaml

# AI Agent (Tier 3)
helm install ai-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-ai.yaml

# Architect Agent (Tier 4)
helm install architect-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-architect.yaml
```

## Customizing Values

### Create Custom Values File

```yaml
# custom-values.yaml
agent:
  name: my-custom-agent
  tier: 3
  type: security
  version: "1.0.0"

image:
  repository: ghcr.io/my-org/my-agent
  tag: "v1.0.0"

resources:
  requests:
    cpu: 1
    memory: 2Gi
  limits:
    cpu: 4
    memory: 8Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10

governance:
  budgetMonthly: 200
  costCenter: engineering
```

### Deploy with Custom Values

```bash
helm install my-agent ai-agent \
  --namespace ai-agents-prod \
  --values custom-values.yaml
```

## Upgrade and Rollback

### Upgrade

```bash
helm upgrade security-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-security.yaml \
  --set image.tag=v2.0.0
```

### Rollback

```bash
# List releases
helm list -n ai-agents-prod

# Rollback to previous version
helm rollback security-agent -n ai-agents-prod

# Rollback to specific revision
helm rollback security-agent 2 -n ai-agents-prod
```

## Testing

### Dry Run

```bash
helm install security-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-security.yaml \
  --dry-run --debug
```

### Template Rendering

```bash
helm template security-agent ai-agent \
  --values ai-agent/values-security.yaml
```

## Uninstall

```bash
helm uninstall security-agent -n ai-agents-prod
```

## Values Files for Each Agent

### Security Agent (`values-security.yaml`)

```yaml
agent:
  name: security-agent
  tier: 3
  type: security
  version: "1.0.0"

image:
  repository: ghcr.io/your-org/security-agent
  tag: "latest"

resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2
    memory: 4Gi

cronjob:
  enabled: true
  schedule: "0 2 * * *"

governance:
  budgetMonthly: 150
  costCenter: security
```

### IT-Ops Agent (`values-itops.yaml`)

```yaml
agent:
  name: it-ops-agent
  tier: 3
  type: it-ops
  version: "1.0.0"

image:
  repository: ghcr.io/your-org/it-ops-agent
  tag: "latest"

resources:
  requests:
    cpu: 1
    memory: 2Gi
  limits:
    cpu: 4
    memory: 8Gi

cronjob:
  enabled: false

governance:
  budgetMonthly: 300
  costCenter: operations
```

### AI Agent (`values-ai.yaml`)

```yaml
agent:
  name: ai-agent
  tier: 3
  type: ai
  version: "1.0.0"

image:
  repository: ghcr.io/your-org/ai-agent
  tag: "latest"

resources:
  requests:
    cpu: 2
    memory: 4Gi
  limits:
    cpu: 8
    memory: 16Gi

persistence:
  enabled: true
  size: 50Gi

cronjob:
  enabled: true
  schedule: "0 0 * * 0"  # Weekly

governance:
  budgetMonthly: 800
  costCenter: ai-ml
```

### Architect Agent (`values-architect.yaml`)

```yaml
agent:
  name: architect-agent
  tier: 4
  type: architect
  version: "1.0.0"

image:
  repository: ghcr.io/your-org/architect-agent
  tag: "latest"

resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2
    memory: 4Gi

cronjob:
  enabled: false

governance:
  budgetMonthly: 350
  costCenter: architecture
```

## Next Steps

1. Customize values files for your environment
2. Build and push Docker images for each agent
3. Deploy to dev environment for testing
4. Run governance checks
5. Deploy to production with approval gates

For more details, see the [Kubernetes Deployment Guide](../../docs/KUBERNETES-DEPLOYMENT-GUIDE.md).
