# AI Agents - Build and Deployment Guide

This directory contains the source code, Docker images, and deployment configurations for 4 specialized AI agents.

## 📁 Directory Structure

```
agents/
├── security/              # Security Agent (Tier 3)
│   ├── src/
│   │   ├── handlers/
│   │   │   ├── api_server.py      # FastAPI server
│   │   │   └── scanner.py         # CronJob scanner
│   │   ├── lib/                   # Shared libraries
│   │   └── config/                # Agent config
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── tests/
│   └── docs/
│
├── it-ops/                # IT-Ops Agent (Tier 3)
│   ├── src/
│   │   ├── handlers/
│   │   │   └── api_server.py      # Long-running service
│   │   ├── lib/
│   │   └── config/
│   ├── docker/
│   ├── tests/
│   └── docs/
│
├── ai/                    # AI Agent (Tier 3)
│   ├── src/
│   │   ├── handlers/
│   │   │   └── training_job.py    # ML training CronJob
│   │   ├── lib/
│   │   └── config/
│   ├── docker/
│   ├── tests/
│   └── docs/
│
├── architect/             # Architect Agent (Tier 4)
│   ├── src/
│   │   ├── handlers/
│   │   │   └── api_server.py      # Long-running service
│   │   ├── lib/
│   │   └── config/
│   ├── docker/
│   ├── tests/
│   └── docs/
│
└── README.md             # This file
```

## 🎯 Agent Overview

| Agent | Tier | Runtime | Purpose | Monthly Cost |
|-------|------|---------|---------|--------------|
| **Security** | 3 | CronJob + Deployment | Vulnerability scanning, compliance | $150 |
| **IT-Ops** | 3 | Deployment (long-running) | Incident response, deployments | $300 |
| **AI** | 3 | CronJob | ML model training | $800 |
| **Architect** | 4 | Deployment (long-running) | System design, reviews | $350 |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Required tools
docker --version          # Docker 20.10+
kubectl version --client  # Kubernetes 1.27+
helm version             # Helm 3.12+

# Verify cluster access
kubectl cluster-info
```

### Build All Agents

```bash
# From repository root
cd /home/suhlabs/projects/ai-agent-governance-framework

# Build Security Agent
docker build -t ghcr.io/your-org/security-agent:latest \
  -f agents/security/docker/Dockerfile .

# Build IT-Ops Agent
docker build -t ghcr.io/your-org/it-ops-agent:latest \
  -f agents/it-ops/docker/Dockerfile .

# Build AI Agent
docker build -t ghcr.io/your-org/ai-agent:latest \
  -f agents/ai/docker/Dockerfile .

# Build Architect Agent
docker build -t ghcr.io/your-org/architect-agent:latest \
  -f agents/architect/docker/Dockerfile .
```

### Push to Container Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u your-username --password-stdin

# Push all images
docker push ghcr.io/your-org/security-agent:latest
docker push ghcr.io/your-org/it-ops-agent:latest
docker push ghcr.io/your-org/ai-agent:latest
docker push ghcr.io/your-org/architect-agent:latest
```

### Deploy to Kubernetes

```bash
# Deploy Security Agent
helm install security-agent deploy/helm/ai-agent \
  --namespace ai-agents-prod \
  --create-namespace \
  --values deploy/helm/ai-agent/values-security.yaml

# Deploy IT-Ops Agent
helm install it-ops-agent deploy/helm/ai-agent \
  --namespace ai-agents-prod \
  --values deploy/helm/ai-agent/values-itops.yaml

# Deploy AI Agent
helm install ai-agent deploy/helm/ai-agent \
  --namespace ai-agents-prod \
  --values deploy/helm/ai-agent/values-ai.yaml

# Deploy Architect Agent
helm install architect-agent deploy/helm/ai-agent \
  --namespace ai-agents-prod \
  --values deploy/helm/ai-agent/values-architect.yaml
```

### Verify Deployments

```bash
# Check pods
kubectl get pods -n ai-agents-prod

# Check services
kubectl get svc -n ai-agents-prod

# View logs
kubectl logs -f deployment/security-agent -n ai-agents-prod
kubectl logs -f deployment/it-ops-agent -n ai-agents-prod
kubectl logs -f deployment/architect-agent -n ai-agents-prod

# Check CronJobs
kubectl get cronjobs -n ai-agents-prod
```

---

## 🐳 Docker Build Details

### Building Individual Agents

#### Security Agent

```bash
cd /home/suhlabs/projects/ai-agent-governance-framework

docker build \
  -t security-agent:dev \
  -f agents/security/docker/Dockerfile \
  --build-arg FRAMEWORK_VERSION=2.1.0 \
  .

# Run locally
docker run -p 8080:8080 -p 9090:9090 \
  -e AGENT_TIER=3 \
  -e FRAMEWORK_VERSION=2.1.0 \
  security-agent:dev
```

#### IT-Ops Agent

```bash
docker build \
  -t it-ops-agent:dev \
  -f agents/it-ops/docker/Dockerfile \
  .

# Run locally
docker run -p 8080:8080 -p 9090:9090 \
  -e AGENT_TIER=3 \
  -e RUNTIME_MODE=long-running \
  it-ops-agent:dev
```

#### AI Agent

```bash
docker build \
  -t ai-agent:dev \
  -f agents/ai/docker/Dockerfile \
  .

# Run training job locally
docker run \
  -v $(pwd)/data:/var/ml-data \
  -e AGENT_TIER=3 \
  ai-agent:dev \
  python -m src.handlers.training_job
```

#### Architect Agent

```bash
docker build \
  -t architect-agent:dev \
  -f agents/architect/docker/Dockerfile \
  .

# Run locally
docker run -p 8080:8080 -p 9090:9090 \
  -e AGENT_TIER=4 \
  architect-agent:dev
```

### Multi-Platform Builds

```bash
# Build for AMD64 and ARM64
docker buildx create --use

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/your-org/security-agent:latest \
  -f agents/security/docker/Dockerfile \
  --push \
  .
```

---

## 🧪 Local Development

### Running with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  security-agent:
    build:
      context: .
      dockerfile: agents/security/docker/Dockerfile
    ports:
      - "8081:8080"
      - "9091:9090"
    environment:
      - AGENT_TIER=3
      - FRAMEWORK_VERSION=2.1.0

  it-ops-agent:
    build:
      context: .
      dockerfile: agents/it-ops/docker/Dockerfile
    ports:
      - "8082:8080"
      - "9092:9090"
    environment:
      - AGENT_TIER=3

  architect-agent:
    build:
      context: .
      dockerfile: agents/architect/docker/Dockerfile
    ports:
      - "8084:8080"
      - "9094:9090"
    environment:
      - AGENT_TIER=4
```

```bash
docker-compose up -d
docker-compose logs -f
```

### Testing Endpoints

```bash
# Security Agent
curl http://localhost:8081/health
curl -X POST http://localhost:8081/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "my-app:latest", "scan_type": "container"}'

# IT-Ops Agent
curl http://localhost:8082/health
curl -X POST http://localhost:8082/incidents \
  -H "Content-Type: application/json" \
  -d '{"severity": "P1", "description": "High CPU usage"}'

# Architect Agent
curl http://localhost:8084/health
curl -X POST http://localhost:8084/design \
  -H "Content-Type: application/json" \
  -d '{"requirements": "E-commerce platform", "system_type": "microservices"}'

# Metrics
curl http://localhost:9091/metrics  # Security
curl http://localhost:9092/metrics  # IT-Ops
curl http://localhost:9094/metrics  # Architect
```

---

## 🔧 Development Workflow

### 1. Make Code Changes

```bash
# Example: Update Security Agent
vim agents/security/src/handlers/api_server.py
```

### 2. Run Tests

```bash
cd agents/security
pytest src/tests/ -v --cov=src
```

### 3. Build and Test Locally

```bash
docker build -t security-agent:dev -f docker/Dockerfile ../..
docker run -p 8080:8080 security-agent:dev
```

### 4. Push to Dev Environment

```bash
# Tag with version
docker tag security-agent:dev ghcr.io/your-org/security-agent:v1.0.1

# Push
docker push ghcr.io/your-org/security-agent:v1.0.1

# Deploy to dev
helm upgrade security-agent deploy/helm/ai-agent \
  --namespace ai-agents-dev \
  --values deploy/helm/ai-agent/values-security.yaml \
  --set image.tag=v1.0.1
```

---

## 🚢 CI/CD Integration

### GitHub Actions Workflow

The repository includes GitHub Actions workflows for automated builds:

- `.github/workflows/build-security-agent.yml`
- `.github/workflows/build-itops-agent.yml`
- `.github/workflows/build-ai-agent.yml`
- `.github/workflows/build-architect-agent.yml`

Each workflow:
1. Runs governance checks
2. Executes security scans
3. Builds Docker image
4. Pushes to container registry
5. Deploys to Kubernetes

### Manual Trigger

```bash
# Trigger via GitHub CLI
gh workflow run build-security-agent.yml \
  -f environment=prod \
  -f version=v1.0.1
```

---

## 📊 Monitoring

### Access Metrics

```bash
# Port-forward Prometheus
kubectl port-forward -n ai-agents-monitoring svc/prometheus-server 9090:80

# Port-forward Grafana
kubectl port-forward -n ai-agents-monitoring svc/grafana 3000:80
```

Open:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

### View Agent Metrics

```bash
# Query Prometheus
curl http://localhost:9090/api/v1/query?query=security_scan_requests_total
curl http://localhost:9090/api/v1/query?query=ops_incident_requests_total
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
kubectl logs deployment/security-agent -n ai-agents-prod

# Describe pod
kubectl describe pod security-agent-xxx -n ai-agents-prod

# Get events
kubectl get events -n ai-agents-prod --sort-by='.lastTimestamp'
```

### Build Failures

```bash
# Ensure you're in repo root
pwd  # Should be /home/suhlabs/projects/ai-agent-governance-framework

# Verify Dockerfile paths
ls agents/security/docker/Dockerfile
ls agents/security/src/handlers/

# Build with no cache
docker build --no-cache -t security-agent:dev \
  -f agents/security/docker/Dockerfile .
```

### Health Check Failures

```bash
# Test health endpoint directly
kubectl exec -it deployment/security-agent -n ai-agents-prod -- \
  curl http://localhost:8080/health
```

---

## 📚 Next Steps

1. **Customize Agents** - Add business logic to handlers
2. **Add Tests** - Write unit and integration tests
3. **Configure Secrets** - Set up External Secrets Operator
4. **Deploy Monitoring** - Install Prometheus + Grafana
5. **Run Governance Checks** - Execute threat modeling
6. **Deploy to Production** - Follow approval workflow

For detailed Kubernetes deployment instructions, see:
- [Kubernetes Deployment Guide](../docs/KUBERNETES-DEPLOYMENT-GUIDE.md)
- [Multi-Repo vs Monorepo Architecture](../docs/MULTI-REPO-VS-MONOREPO-ARCHITECTURE.md)

---

**Built with AI Agent Governance Framework v2.1.0**
