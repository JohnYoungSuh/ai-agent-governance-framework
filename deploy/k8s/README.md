# Kubernetes Deployment Guide

This directory contains all Kubernetes deployment manifests for the AI Agent Governance Framework.

## Directory Structure

```
k8s/
├── base/                              # Base Kubernetes manifests
│   ├── namespaces.yaml                # Namespace definitions
│   ├── resource-quotas.yaml           # Resource quotas and limits
│   ├── security-agent-deployment.yaml # Security Agent (example)
│   └── kustomization.yaml             # Kustomize base config
│
├── overlays/                          # Environment-specific overlays
│   ├── dev/
│   │   ├── kustomization.yaml         # Dev environment config
│   │   ├── patches/                   # Dev-specific patches
│   │   └── secrets/                   # Dev secrets (External Secrets)
│   ├── staging/
│   │   ├── kustomization.yaml         # Staging environment config
│   │   ├── patches/                   # Staging-specific patches
│   │   └── secrets/                   # Staging secrets
│   └── prod/
│       ├── kustomization.yaml         # Production environment config
│       ├── patches/                   # Prod-specific patches
│       └── secrets/                   # Production secrets
│
└── README.md                          # This file
```

## Quick Start

### 1. Deploy Namespaces and Resource Quotas

```bash
kubectl apply -f base/namespaces.yaml
kubectl apply -f base/resource-quotas.yaml
```

### 2. Deploy Security Agent (Example)

**Using Kustomize:**
```bash
# Development
kubectl apply -k overlays/dev/

# Production
kubectl apply -k overlays/prod/
```

**Using kubectl directly:**
```bash
kubectl apply -f base/security-agent-deployment.yaml
```

### 3. Verify Deployment

```bash
# Check pods
kubectl get pods -n ai-agents-prod

# Check services
kubectl get svc -n ai-agents-prod

# Check logs
kubectl logs -f deployment/security-agent -n ai-agents-prod
```

## Environment-Specific Configuration

### Development
- Namespace: `ai-agents-dev`
- Resource Limits: 16 vCPU, 32Gi RAM
- Replicas: 1
- Auto-scaling: Disabled

### Staging
- Namespace: `ai-agents-staging`
- Resource Limits: 32 vCPU, 64Gi RAM
- Replicas: 2
- Auto-scaling: Enabled (2-3 replicas)

### Production
- Namespace: `ai-agents-prod`
- Resource Limits: 64 vCPU, 128Gi RAM
- Replicas: 2-5
- Auto-scaling: Enabled (2-5 replicas)

## Deployment Commands

### Deploy All Agents to Production

```bash
# Using Helm (recommended)
helm upgrade --install security-agent ../helm/ai-agent \
  --namespace ai-agents-prod \
  --values ../helm/ai-agent/values-security.yaml \
  --wait

helm upgrade --install it-ops-agent ../helm/ai-agent \
  --namespace ai-agents-prod \
  --values ../helm/ai-agent/values-itops.yaml \
  --wait

helm upgrade --install ai-agent ../helm/ai-agent \
  --namespace ai-agents-prod \
  --values ../helm/ai-agent/values-ai.yaml \
  --wait

helm upgrade --install architect-agent ../helm/ai-agent \
  --namespace ai-agents-prod \
  --values ../helm/ai-agent/values-architect.yaml \
  --wait
```

### Rollback

```bash
# Helm rollback
helm rollback security-agent -n ai-agents-prod

# Kubernetes rollback
kubectl rollout undo deployment/security-agent -n ai-agents-prod
```

## Monitoring

### Check Resource Usage

```bash
kubectl top nodes
kubectl top pods -n ai-agents-prod
```

### View Metrics

```bash
# Port-forward Prometheus
kubectl port-forward -n ai-agents-monitoring svc/prometheus-server 9090:80

# Port-forward Grafana
kubectl port-forward -n ai-agents-monitoring svc/grafana 3000:80
```

## Troubleshooting

See the main [Kubernetes Deployment Guide](../../docs/KUBERNETES-DEPLOYMENT-GUIDE.md) for detailed troubleshooting steps.

## Next Steps

1. Review [Kubernetes Deployment Guide](../../docs/KUBERNETES-DEPLOYMENT-GUIDE.md)
2. Customize Helm values for your agents
3. Set up External Secrets Operator for secret management
4. Configure monitoring and alerting
5. Deploy to dev environment first
6. Run governance checks and threat modeling
7. Deploy to production after approval
