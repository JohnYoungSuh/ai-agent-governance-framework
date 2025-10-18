# Kubernetes Deployment Guide
## AI Agent Governance Framework - Kubernetes Architecture

**Version:** 1.0
**Date:** October 2025
**Status:** Production Ready

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Kubernetes Architecture Design](#3-kubernetes-architecture-design)
4. [Agent Deployment Specifications](#4-agent-deployment-specifications)
5. [Namespace Strategy](#5-namespace-strategy)
6. [Resource Quotas & Limits](#6-resource-quotas--limits)
7. [Secrets Management](#7-secrets-management)
8. [Observability & Monitoring](#8-observability--monitoring)
9. [Cost Tracking](#9-cost-tracking)
10. [CI/CD Pipeline](#10-cicd-pipeline)
11. [Deployment Instructions](#11-deployment-instructions)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Architecture Overview

### 1.1 Deployment Model

This guide provides a **Kubernetes-native deployment architecture** for the AI Agent Governance Framework, deploying 4 specialized agents as containerized services.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes Cluster                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Namespace  │  │   Namespace  │  │   Namespace  │         │
│  │  ai-agents-  │  │  ai-agents-  │  │  ai-agents-  │         │
│  │     dev      │  │   staging    │  │     prod     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                 │                 │                   │
│  ┌──────▼─────────────────▼─────────────────▼──────────┐       │
│  │          4 Agent Deployments per Namespace          │       │
│  │  ┌─────────────┐  ┌─────────────┐                 │       │
│  │  │  Security   │  │   IT-Ops    │                 │       │
│  │  │    Agent    │  │    Agent    │                 │       │
│  │  │  (Tier 3)   │  │  (Tier 3)   │                 │       │
│  │  └─────────────┘  └─────────────┘                 │       │
│  │  ┌─────────────┐  ┌─────────────┐                 │       │
│  │  │     AI      │  │  Architect  │                 │       │
│  │  │    Agent    │  │    Agent    │                 │       │
│  │  │  (Tier 3)   │  │  (Tier 4)   │                 │       │
│  │  └─────────────┘  └─────────────┘                 │       │
│  └────────────────────────────────────────────────────┘       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │         Shared Infrastructure Components             │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │     │
│  │  │Prometheus│  │ Grafana  │  │  Jaeger  │           │     │
│  │  │Monitoring│  │Dashboard │  │ Tracing  │           │     │
│  │  └──────────┘  └──────────┘  └──────────┘           │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              External Dependencies                   │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │     │
│  │  │PostgreSQL│  │  Redis   │  │   S3     │           │     │
│  │  │ (Audit)  │  │ (Cache)  │  │(Evidence)│           │     │
│  │  └──────────┘  └──────────┘  └──────────┘           │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Orchestration** | Kubernetes | Industry standard, portable, auto-scaling |
| **Package Manager** | Helm + Kustomize | Helm for templating, Kustomize for overlays |
| **Service Mesh** | Optional (Istio/Linkerd) | For advanced traffic management |
| **Secrets** | Kubernetes Secrets + External Secrets Operator | Native K8s + cloud integration |
| **Monitoring** | Prometheus + Grafana | OpenTelemetry compatible |
| **Tracing** | Jaeger | Distributed tracing for agent workflows |
| **Logging** | Fluentd/Fluent Bit → ELK/Loki | Centralized log aggregation |
| **Ingress** | NGINX Ingress Controller | HTTP routing and TLS termination |
| **Storage** | PostgreSQL (audit), Redis (cache), S3 (evidence) | Persistent data requirements |

---

## 2. Prerequisites

### 2.1 Required Tools

```bash
# Kubernetes CLI
kubectl version --client

# Helm (package manager)
helm version

# Kustomize (configuration management)
kustomize version

# Docker (container builds)
docker version

# Optional: K9s (terminal UI)
k9s version
```

### 2.2 Cluster Requirements

**Minimum Cluster Specifications:**

| Environment | Nodes | vCPU | Memory | Storage |
|-------------|-------|------|--------|---------|
| Development | 3 | 8 | 16 GB | 100 GB |
| Staging | 3 | 16 | 32 GB | 200 GB |
| Production | 5 | 32 | 64 GB | 500 GB |

**Kubernetes Version:** >= 1.27

**Supported Platforms:**
- AWS EKS
- Google GKE
- Azure AKS
- On-premises (kubeadm, k3s, RKE)

### 2.3 Access Requirements

```bash
# Verify cluster access
kubectl cluster-info

# Check permissions
kubectl auth can-i create deployments --all-namespaces
kubectl auth can-i create secrets --all-namespaces
kubectl auth can-i create persistentvolumeclaims --all-namespaces
```

---

## 3. Kubernetes Architecture Design

### 3.1 Component Architecture

Each agent consists of:

1. **Deployment** - Pod management and scaling
2. **Service** - Internal networking
3. **ConfigMap** - Non-sensitive configuration
4. **Secret** - Sensitive credentials (API keys, tokens)
5. **PersistentVolumeClaim** - Optional persistent storage
6. **HorizontalPodAutoscaler** - Auto-scaling based on metrics
7. **NetworkPolicy** - Network isolation and security
8. **ServiceAccount** - RBAC permissions

### 3.2 Agent Runtime Models

**Two deployment modes supported:**

#### A. Long-Running Services (API Servers)

```yaml
# Agents that expose HTTP/gRPC APIs
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: security-agent
        image: security-agent:latest
        ports:
        - containerPort: 8080
          name: http
```

#### B. Batch Jobs (CronJobs)

```yaml
# Agents that run scheduled tasks
apiVersion: batch/v1
kind: CronJob
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: security-agent
            image: security-agent:latest
```

### 3.3 Recommended Deployment Mode per Agent

| Agent | Runtime Type | Rationale |
|-------|--------------|-----------|
| **Security Agent** | CronJob + Deployment | Scheduled scans + on-demand API |
| **IT-Ops Agent** | Deployment | Real-time incident response |
| **AI Agent** | CronJob | Scheduled ML training jobs |
| **Architect Agent** | Deployment | On-demand design reviews |

---

## 4. Agent Deployment Specifications

### 4.1 Security Agent (Tier 3)

**Purpose:** Vulnerability scanning, compliance checking, security audits

**Resource Requirements:**
- **CPU:** 500m (request) / 2 (limit)
- **Memory:** 1Gi (request) / 4Gi (limit)
- **Storage:** 10Gi (scan reports)

**Deployment Type:** Hybrid (CronJob + Deployment)

**Key Features:**
- Daily vulnerability scans (CronJob)
- On-demand security audits (Deployment with API)
- Integration with Trivy, Grype, Checkov

### 4.2 IT-Ops Agent (Tier 3)

**Purpose:** Deployment automation, incident response, infrastructure scaling

**Resource Requirements:**
- **CPU:** 1 (request) / 4 (limit)
- **Memory:** 2Gi (request) / 8Gi (limit)
- **Storage:** 5Gi (logs)

**Deployment Type:** Long-Running Service

**Key Features:**
- Real-time incident detection and response
- Automated runbook execution
- Integration with Kubernetes API, Prometheus AlertManager

### 4.3 AI Agent (Tier 3)

**Purpose:** ML model training, deployment, monitoring

**Resource Requirements:**
- **CPU:** 2 (request) / 8 (limit)
- **Memory:** 4Gi (request) / 16Gi (limit)
- **GPU:** Optional (1x NVIDIA T4 for training)
- **Storage:** 50Gi (model artifacts)

**Deployment Type:** CronJob (training) + Deployment (serving)

**Key Features:**
- Scheduled model training jobs
- Model deployment and versioning
- Integration with MLflow, Kubeflow

### 4.4 Architect Agent (Tier 4)

**Purpose:** System design, technical evaluation, architectural decisions

**Resource Requirements:**
- **CPU:** 500m (request) / 2 (limit)
- **Memory:** 1Gi (request) / 4Gi (limit)
- **Storage:** 5Gi (design artifacts)

**Deployment Type:** Long-Running Service

**Key Features:**
- On-demand design reviews
- Architectural pattern recommendations
- Integration with design tools (Mermaid, PlantUML)

---

## 5. Namespace Strategy

### 5.1 Namespace Layout

```yaml
# Three environments, each with 4 agents
namespaces:
  - ai-agents-dev       # Development environment
  - ai-agents-staging   # Staging environment
  - ai-agents-prod      # Production environment
  - ai-agents-monitoring  # Shared monitoring stack
  - ai-agents-system    # Shared infrastructure (PostgreSQL, Redis)
```

### 5.2 Namespace Configuration

Each namespace has:
- **ResourceQuota** - Limit total resources
- **LimitRange** - Default resource limits per pod
- **NetworkPolicy** - Network isolation rules
- **RBAC** - Role-based access control

---

## 6. Resource Quotas & Limits

### 6.1 Namespace Resource Quotas

**Development Environment:**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: ai-agents-dev
spec:
  hard:
    requests.cpu: "8"
    requests.memory: 16Gi
    limits.cpu: "16"
    limits.memory: 32Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"
```

**Production Environment:**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: ai-agents-prod
spec:
  hard:
    requests.cpu: "32"
    requests.memory: 64Gi
    limits.cpu: "64"
    limits.memory: 128Gi
    persistentvolumeclaims: "20"
    services.loadbalancers: "5"
```

### 6.2 Cost Tracking Integration

Map Kubernetes resource costs to framework tier budgets:

| Agent | Tier | Monthly K8s Cost (prod) | Monthly AI Cost | Total |
|-------|------|------------------------|-----------------|-------|
| Security | 3 | $50 (2 vCPU, 4GB) | $100 | $150 |
| IT-Ops | 3 | $100 (4 vCPU, 8GB) | $200 | $300 |
| AI | 3 | $300 (8 vCPU, 16GB, GPU) | $500 | $800 |
| Architect | 4 | $50 (2 vCPU, 4GB) | $300 | $350 |
| **Total** | - | **$500** | **$1,100** | **$1,600** |

---

## 7. Secrets Management

### 7.1 Strategy

Use **External Secrets Operator** to sync secrets from cloud providers:

```
AWS Secrets Manager  ──┐
Azure Key Vault      ──┤
GCP Secret Manager   ──┤──> External Secrets Operator ──> Kubernetes Secrets
HashiCorp Vault      ──┘
```

### 7.2 Secret Structure

**Framework Secrets (per namespace):**
```
/ai-agents/{env}/shared/
  ├── audit-trail-db-password
  ├── redis-password
  ├── s3-access-key
  └── observability-api-key
```

**Agent Secrets (per agent):**
```
/ai-agents/{env}/security-agent/
  ├── trivy-api-token
  ├── github-token
  └── slack-webhook-url

/ai-agents/{env}/it-ops-agent/
  ├── k8s-api-token
  ├── aws-credentials
  └── pagerduty-api-key

/ai-agents/{env}/ai-agent/
  ├── mlflow-tracking-uri
  ├── model-registry-key
  └── training-data-s3-key

/ai-agents/{env}/architect-agent/
  ├── openai-api-key
  ├── confluence-token
  └── jira-api-token
```

---

## 8. Observability & Monitoring

### 8.1 OpenTelemetry Stack

```
┌──────────────────────────────────────────────────────────┐
│                    Agent Pods                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │Security │  │ IT-Ops  │  │   AI    │  │Architect│    │
│  │  Agent  │  │  Agent  │  │  Agent  │  │  Agent  │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘    │
│       │            │            │            │          │
│       └────────────┴────────────┴────────────┘          │
│                        │                                 │
│              OpenTelemetry Collector                     │
│                  (DaemonSet)                             │
│                        │                                 │
│       ┌────────────────┼────────────────┐               │
│       │                │                │               │
│   Prometheus       Jaeger           Loki/ELK           │
│   (Metrics)       (Traces)         (Logs)              │
│       │                │                │               │
│       └────────────────┴────────────────┘               │
│                        │                                 │
│                    Grafana                               │
│              (Unified Dashboard)                         │
└──────────────────────────────────────────────────────────┘
```

### 8.2 Key Metrics to Track

**Per-Agent Metrics:**
- `agent_tasks_total` - Total tasks executed
- `agent_task_duration_seconds` - Task execution time
- `agent_task_cost_dollars` - Cost per task
- `agent_errors_total` - Error count
- `agent_governance_violations_total` - Policy violations

**Cluster-Level Metrics:**
- `pod_cpu_usage` - CPU utilization
- `pod_memory_usage` - Memory utilization
- `pod_network_receive_bytes` - Network ingress
- `pod_network_transmit_bytes` - Network egress

### 8.3 Alerting Rules

```yaml
# Prometheus alert rules
groups:
- name: ai-agents
  rules:
  - alert: HighErrorRate
    expr: rate(agent_errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "Agent {{ $labels.agent_name }} error rate > 10%"

  - alert: BudgetExceeded
    expr: agent_monthly_cost_dollars > agent_budget_limit_dollars
    annotations:
      summary: "Agent {{ $labels.agent_name }} exceeded budget"

  - alert: HighCPUUsage
    expr: pod_cpu_usage > 0.8
    for: 10m
    annotations:
      summary: "Pod {{ $labels.pod }} CPU usage > 80%"
```

---

## 9. Cost Tracking

### 9.1 Cost Attribution

Use **Kubernetes labels** for cost tracking:

```yaml
metadata:
  labels:
    app: security-agent
    tier: "3"
    cost-center: "security"
    team: "devops"
    framework-version: "2.1.0"
```

### 9.2 Cost Monitoring Tools

**Option 1: Kubecost (Recommended)**
```bash
helm install kubecost kubecost/cost-analyzer \
  --namespace kubecost \
  --set prometheus.server.global.external_labels.cluster_id=ai-agents-prod
```

**Option 2: OpenCost**
```bash
kubectl apply -f https://raw.githubusercontent.com/opencost/opencost/develop/kubernetes/opencost.yaml
```

### 9.3 Cost Dashboard

Grafana dashboard showing:
- Cost per agent (daily/monthly)
- Cost per tier
- Cost per namespace (environment)
- Budget vs. actual spend
- Cost per API request

---

## 10. CI/CD Pipeline

### 10.1 GitHub Actions Workflow

The CI/CD pipeline integrates Kubernetes deployment with governance checks:

```yaml
# .github/workflows/deploy-k8s-security-agent.yml
name: Deploy Security Agent to Kubernetes

on:
  push:
    branches: [main]
    paths:
      - 'agents/security/**'
      - 'framework/**'
      - 'deploy/k8s/**'

env:
  AGENT_NAME: security-agent
  AGENT_TIER: 3

jobs:
  # Stage 1: Governance & Security
  governance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate agent configuration
        run: |
          python3 framework/scripts/validate-agent-config.py \
            --config agents/security/k8s/config.yaml \
            --tier 3

      - name: Check budget compliance
        run: |
          ./framework/scripts/compliance-check.sh \
            --agent security-agent --tier 3 --budget-limit 150

      - name: Security scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: 'agents/security'

  # Stage 2: Build & Push Container
  build:
    needs: governance-check
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/security-agent
          tags: |
            type=sha,prefix={{branch}}-
            type=ref,event=branch
            type=semver,pattern={{version}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: agents/security/docker/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Stage 3: Deploy to Dev
  deploy-dev:
    needs: build
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4

      - name: Install kubectl
        uses: azure/setup-kubectl@v3

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG_DEV }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy with Kustomize
        run: |
          cd deploy/k8s/overlays/dev
          kustomize edit set image security-agent=${{ needs.build.outputs.image-tag }}
          kubectl apply -k .

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/security-agent -n ai-agents-dev

      - name: Run smoke tests
        run: |
          kubectl run -n ai-agents-dev smoke-test \
            --image=curlimages/curl:latest \
            --restart=Never \
            --rm -i \
            -- curl http://security-agent:8080/health

  # Stage 4: Deploy to Production (manual approval)
  deploy-prod:
    needs: [build, deploy-dev]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Configure kubectl
        run: |
          echo "${{ secrets.KUBECONFIG_PROD }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig

      - name: Deploy with Helm
        run: |
          helm upgrade --install security-agent \
            deploy/helm/ai-agent \
            --namespace ai-agents-prod \
            --values deploy/helm/ai-agent/values-prod.yaml \
            --set image.tag=${{ needs.build.outputs.image-tag }} \
            --set agent.name=security-agent \
            --set agent.tier=3 \
            --wait

      - name: Record audit event
        run: |
          kubectl exec -n ai-agents-prod deployment/audit-recorder -- \
            /app/record-event.sh \
            --agent security-agent \
            --event DEPLOYMENT \
            --user "${{ github.actor }}" \
            --commit "${{ github.sha }}"
```

---

## 11. Deployment Instructions

### 11.1 Initial Setup

See the detailed deployment manifests in the next section.

### 11.2 Quick Start

```bash
# 1. Create namespaces
kubectl apply -f deploy/k8s/base/namespaces.yaml

# 2. Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets-system \
  --create-namespace

# 3. Deploy monitoring stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace ai-agents-monitoring \
  --create-namespace

# 4. Deploy agents with Helm
cd deploy/helm
helm install security-agent ai-agent \
  --namespace ai-agents-prod \
  --values ai-agent/values-security.yaml

# 5. Verify deployments
kubectl get pods -n ai-agents-prod
kubectl get services -n ai-agents-prod
```

---

## 12. Troubleshooting

### 12.1 Common Issues

**Issue: Pods stuck in Pending**
```bash
# Check events
kubectl describe pod <pod-name> -n ai-agents-prod

# Common causes:
# - Insufficient resources
# - PVC not bound
# - Image pull errors
```

**Issue: High memory usage**
```bash
# Check memory metrics
kubectl top pods -n ai-agents-prod

# Adjust limits
kubectl set resources deployment security-agent \
  --limits=memory=8Gi \
  -n ai-agents-prod
```

**Issue: Service not reachable**
```bash
# Check service endpoints
kubectl get endpoints security-agent -n ai-agents-prod

# Test connectivity
kubectl run -n ai-agents-prod debug \
  --image=nicolaka/netshoot \
  --rm -it -- curl http://security-agent:8080/health
```

### 12.2 Debugging Commands

```bash
# View logs
kubectl logs -f deployment/security-agent -n ai-agents-prod

# Get shell in pod
kubectl exec -it deployment/security-agent -n ai-agents-prod -- /bin/bash

# View events
kubectl get events -n ai-agents-prod --sort-by='.lastTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods -n ai-agents-prod
```

---

## Next Steps

1. Review the Kubernetes manifests in `deploy/k8s/`
2. Customize Helm values in `deploy/helm/ai-agent/values-*.yaml`
3. Deploy to dev environment first
4. Run governance checks and threat modeling
5. Deploy to production after approval

**Complete manifests and Helm charts are provided in the following sections.**
