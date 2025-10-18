# Complete Deployment Guide
## AI Agent Governance Framework - Kubernetes Deployment

**Version:** 1.0
**Date:** October 2025
**Status:** Production Ready

---

## 🎯 Quick Deployment (5 Steps)

```bash
# From repository root
cd /home/suhlabs/projects/ai-agent-governance-framework

# Step 1: Deploy External Secrets Operator
./scripts/deploy-external-secrets.sh

# Step 2: Deploy Monitoring Stack
./scripts/deploy-monitoring.sh

# Step 3: Build Docker Images
docker build -t ghcr.io/your-org/security-agent:latest -f agents/security/docker/Dockerfile .
docker build -t ghcr.io/your-org/it-ops-agent:latest -f agents/it-ops/docker/Dockerfile .
docker build -t ghcr.io/your-org/ai-agent:latest -f agents/ai/docker/Dockerfile .
docker build -t ghcr.io/your-org/architect-agent:latest -f agents/architect/docker/Dockerfile .

# Step 4: Push Images
docker push ghcr.io/your-org/security-agent:latest
docker push ghcr.io/your-org/it-ops-agent:latest
docker push ghcr.io/your-org/ai-agent:latest
docker push ghcr.io/your-org/architect-agent:latest

# Step 5: Deploy Agents
./scripts/deploy-agents.sh dev
```

---

## 📋 Complete Step-by-Step Deployment

### Prerequisites

**Required Tools:**
- kubectl 1.27+
- helm 3.12+
- docker 20.10+
- AWS CLI (for secrets)

**Cluster Requirements:**
- Kubernetes 1.27+
- 3+ nodes (production)
- 32+ vCPU, 64Gi+ RAM (production)

**Verify Access:**
```bash
kubectl cluster-info
kubectl get nodes
```

---

### Step 1: External Secrets Operator

**1.1 Deploy Operator:**
```bash
./scripts/deploy-external-secrets.sh
```

**1.2 Create AWS Secrets:**
```bash
# Security Agent secrets
aws secretsmanager create-secret \
  --name ai-agents/prod/security-agent \
  --secret-string '{
    "trivy-api-token": "YOUR_TOKEN",
    "github-token": "YOUR_GITHUB_TOKEN",
    "slack-webhook-url": "YOUR_WEBHOOK_URL"
  }'

# IT-Ops Agent secrets
aws secretsmanager create-secret \
  --name ai-agents/prod/it-ops-agent \
  --secret-string '{
    "k8s-api-token": "YOUR_TOKEN",
    "aws-access-key-id": "YOUR_KEY",
    "aws-secret-access-key": "YOUR_SECRET",
    "pagerduty-api-key": "YOUR_PAGERDUTY_KEY"
  }'

# AI Agent secrets
aws secretsmanager create-secret \
  --name ai-agents/prod/ai-agent \
  --secret-string '{
    "mlflow-tracking-uri": "http://mlflow:5000",
    "model-registry-key": "YOUR_KEY",
    "s3-access-key": "YOUR_KEY"
  }'

# Architect Agent secrets
aws secretsmanager create-secret \
  --name ai-agents/prod/architect-agent \
  --secret-string '{
    "openai-api-key": "YOUR_OPENAI_KEY",
    "anthropic-api-key": "YOUR_ANTHROPIC_KEY",
    "jira-api-token": "YOUR_JIRA_TOKEN",
    "confluence-token": "YOUR_CONFLUENCE_TOKEN"
  }'

# Shared secrets
aws secretsmanager create-secret \
  --name ai-agents/prod/shared \
  --secret-string '{
    "postgres_password": "YOUR_PASSWORD",
    "redis_password": "YOUR_PASSWORD",
    "s3_access_key": "YOUR_KEY",
    "s3_secret_key": "YOUR_SECRET"
  }'
```

**1.3 Configure IRSA (EKS only):**
```bash
eksctl create iamserviceaccount \
  --name external-secrets-sa \
  --namespace ai-agents-prod \
  --cluster YOUR_CLUSTER_NAME \
  --attach-policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite \
  --approve \
  --override-existing-serviceaccounts
```

**1.4 Update Account ID:**
```bash
# Edit deploy/k8s/base/external-secrets.yaml
# Replace ACCOUNT_ID with your AWS account ID
sed -i 's/ACCOUNT_ID/123456789012/g' deploy/k8s/base/external-secrets.yaml
```

**1.5 Apply External Secrets:**
```bash
kubectl apply -f deploy/k8s/base/external-secrets.yaml
```

**1.6 Verify:**
```bash
kubectl get externalsecrets -n ai-agents-prod
kubectl get secrets -n ai-agents-prod
```

---

### Step 2: Monitoring Stack

**2.1 Deploy Prometheus + Grafana:**
```bash
./scripts/deploy-monitoring.sh
```

**2.2 Access Grafana:**
```bash
# Port-forward
kubectl port-forward -n ai-agents-monitoring svc/prometheus-grafana 3000:80

# Get password
kubectl get secret -n ai-agents-monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode

# Open http://localhost:3000
# Username: admin
# Password: <from above>
```

**2.3 Import Dashboards:**

In Grafana UI:
1. Go to Dashboards → Import
2. Import these dashboard IDs:
   - **315** - Kubernetes Cluster Monitoring
   - **3119** - Kubernetes Pod Metrics
   - **6417** - Kubernetes Cluster Monitoring (via Prometheus)

**2.4 Verify Metrics:**
```bash
# Port-forward Prometheus
kubectl port-forward -n ai-agents-monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Open http://localhost:9090
# Query: up{namespace="ai-agents-prod"}
```

---

### Step 3: Build Docker Images

**3.1 Configure Registry:**
```bash
# GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Update image repository in Helm values
export ORG_NAME="your-org"
find deploy/helm/ai-agent -name "values-*.yaml" -exec sed -i "s/your-org/$ORG_NAME/g" {} \;
```

**3.2 Build All Images:**
```bash
# From repository root
cd /home/suhlabs/projects/ai-agent-governance-framework

# Security Agent
docker build \
  -t ghcr.io/$ORG_NAME/security-agent:v1.0.0 \
  -t ghcr.io/$ORG_NAME/security-agent:latest \
  -f agents/security/docker/Dockerfile .

# IT-Ops Agent
docker build \
  -t ghcr.io/$ORG_NAME/it-ops-agent:v1.0.0 \
  -t ghcr.io/$ORG_NAME/it-ops-agent:latest \
  -f agents/it-ops/docker/Dockerfile .

# AI Agent
docker build \
  -t ghcr.io/$ORG_NAME/ai-agent:v1.0.0 \
  -t ghcr.io/$ORG_NAME/ai-agent:latest \
  -f agents/ai/docker/Dockerfile .

# Architect Agent
docker build \
  -t ghcr.io/$ORG_NAME/architect-agent:v1.0.0 \
  -t ghcr.io/$ORG_NAME/architect-agent:latest \
  -f agents/architect/docker/Dockerfile .
```

**3.3 Push Images:**
```bash
docker push ghcr.io/$ORG_NAME/security-agent:v1.0.0
docker push ghcr.io/$ORG_NAME/security-agent:latest

docker push ghcr.io/$ORG_NAME/it-ops-agent:v1.0.0
docker push ghcr.io/$ORG_NAME/it-ops-agent:latest

docker push ghcr.io/$ORG_NAME/ai-agent:v1.0.0
docker push ghcr.io/$ORG_NAME/ai-agent:latest

docker push ghcr.io/$ORG_NAME/architect-agent:v1.0.0
docker push ghcr.io/$ORG_NAME/architect-agent:latest
```

---

### Step 4: Deploy to Dev Environment

**4.1 Run Governance Checks:**
```bash
./scripts/governance-check.sh --agent security-agent --tier 3 --environment dev --budget-limit 150
./scripts/governance-check.sh --agent it-ops-agent --tier 3 --environment dev --budget-limit 300
./scripts/governance-check.sh --agent ai-agent --tier 3 --environment dev --budget-limit 800
./scripts/governance-check.sh --agent architect-agent --tier 4 --environment dev --budget-limit 350
```

**4.2 Deploy All Agents:**
```bash
./scripts/deploy-agents.sh dev
```

**4.3 Verify Deployments:**
```bash
# Check pods
kubectl get pods -n ai-agents-dev

# Expected output:
# NAME                              READY   STATUS    RESTARTS   AGE
# security-agent-xxx                1/1     Running   0          1m
# it-ops-agent-xxx                  1/1     Running   0          1m
# architect-agent-xxx               1/1     Running   0          1m

# Check services
kubectl get svc -n ai-agents-dev

# Check CronJobs
kubectl get cronjobs -n ai-agents-dev

# View logs
kubectl logs -f deployment/security-agent -n ai-agents-dev
```

**4.4 Test Endpoints:**
```bash
# Port-forward Security Agent
kubectl port-forward -n ai-agents-dev svc/security-agent 8080:8080

# Test health endpoint
curl http://localhost:8080/health

# Test scan endpoint
curl -X POST http://localhost:8080/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "nginx:latest", "scan_type": "container"}'
```

---

### Step 5: Run Threat Modeling (Tier 3+ Only)

**5.1 Run Threat Model for Each Agent:**
```bash
# Security Agent
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent security-agent \
  --tier 3

# IT-Ops Agent
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent it-ops-agent \
  --tier 3

# AI Agent
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent ai-agent \
  --tier 3

# Architect Agent
./workflows/threat-modeling/scripts/run-threat-model.sh \
  --agent architect-agent \
  --tier 4
```

**5.2 Review Reports:**
```bash
cat workflows/threat-modeling/reports/security-agent-threat-model.md
cat workflows/threat-modeling/reports/it-ops-agent-threat-model.md
cat workflows/threat-modeling/reports/ai-agent-threat-model.md
cat workflows/threat-modeling/reports/architect-agent-threat-model.md
```

---

### Step 6: Deploy to Staging

**6.1 Update Image Tags:**
```bash
# Tag dev images as staging
docker tag ghcr.io/$ORG_NAME/security-agent:latest ghcr.io/$ORG_NAME/security-agent:staging
docker tag ghcr.io/$ORG_NAME/it-ops-agent:latest ghcr.io/$ORG_NAME/it-ops-agent:staging
docker tag ghcr.io/$ORG_NAME/ai-agent:latest ghcr.io/$ORG_NAME/ai-agent:staging
docker tag ghcr.io/$ORG_NAME/architect-agent:latest ghcr.io/$ORG_NAME/architect-agent:staging

# Push
docker push ghcr.io/$ORG_NAME/security-agent:staging
docker push ghcr.io/$ORG_NAME/it-ops-agent:staging
docker push ghcr.io/$ORG_NAME/ai-agent:staging
docker push ghcr.io/$ORG_NAME/architect-agent:staging
```

**6.2 Deploy to Staging:**
```bash
./scripts/deploy-agents.sh staging
```

**6.3 Run Integration Tests:**
```bash
# Test agent interactions
kubectl run -n ai-agents-staging integration-test \
  --image=curlimages/curl:latest \
  --restart=Never \
  --rm -i -- sh -c '
    curl -f http://security-agent:8080/health &&
    curl -f http://it-ops-agent:8080/health &&
    curl -f http://architect-agent:8080/health
  '
```

---

### Step 7: Deploy to Production (with Approval)

**7.1 Manual Approval Required**

Production deployments require:
- ✅ All governance checks passed
- ✅ Threat models completed and reviewed
- ✅ Staging tests passed
- ✅ Budget approved
- ✅ Security team approval

**7.2 GitHub Actions Deployment (Recommended):**
```bash
# Trigger via GitHub UI or CLI
gh workflow run deploy-security-agent.yml \
  -f environment=prod \
  -f image_tag=v1.0.0
```

**7.3 Manual Deployment:**
```bash
# Tag for production
docker tag ghcr.io/$ORG_NAME/security-agent:staging ghcr.io/$ORG_NAME/security-agent:v1.0.0
docker push ghcr.io/$ORG_NAME/security-agent:v1.0.0

# Deploy
helm upgrade --install security-agent deploy/helm/ai-agent \
  --namespace ai-agents-prod \
  --values deploy/helm/ai-agent/values-security.yaml \
  --set image.tag=v1.0.0 \
  --wait \
  --timeout 10m
```

**7.4 Post-Deployment Validation:**
```bash
# Verify all pods running
kubectl get pods -n ai-agents-prod

# Check metrics
kubectl port-forward -n ai-agents-prod svc/security-agent 9090:9090
curl http://localhost:9090/metrics

# Monitor logs for 10 minutes
kubectl logs -f deployment/security-agent -n ai-agents-prod --tail=100
```

---

## 🔍 Monitoring & Observability

### Access Dashboards

**Grafana:**
```bash
kubectl port-forward -n ai-agents-monitoring svc/prometheus-grafana 3000:80
# http://localhost:3000
```

**Prometheus:**
```bash
kubectl port-forward -n ai-agents-monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# http://localhost:9090
```

**AlertManager:**
```bash
kubectl port-forward -n ai-agents-monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093
# http://localhost:9093
```

### Key Metrics to Monitor

```promql
# Agent health
up{namespace="ai-agents-prod"}

# Request rates
rate(security_scan_requests_total[5m])
rate(ops_incident_requests_total[5m])
rate(architect_design_requests_total[5m])

# Error rates
rate(security_scan_errors[5m])
rate(ops_deployment_failures[5m])

# Response times
histogram_quantile(0.95, ops_response_time_seconds_bucket)

# Resource usage
container_cpu_usage_seconds_total{namespace="ai-agents-prod"}
container_memory_usage_bytes{namespace="ai-agents-prod"}

# Cost tracking
agent_monthly_cost_dollars
agent_budget_limit_dollars
```

---

## 🐛 Troubleshooting

See [Kubernetes Deployment Guide](docs/KUBERNETES-DEPLOYMENT-GUIDE.md#12-troubleshooting) for detailed troubleshooting.

---

## 📚 Next Steps

1. ✅ **Monitor agents** - Watch Grafana dashboards
2. ✅ **Configure alerts** - Set up Slack/PagerDuty notifications
3. ✅ **Optimize costs** - Review budget usage
4. ✅ **Add custom logic** - Enhance agent handlers
5. ✅ **Scale as needed** - Adjust HPA settings

---

**Deployment Complete! 🎉**

Your AI Agent Governance Framework is now running on Kubernetes with full observability, security, and governance.
