# CMDB Deployment Guide

AI Agent Governance Framework - Internal v2.1

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Configuration](#configuration)
6. [Monitoring and Health Checks](#monitoring-and-health-checks)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Software Requirements

- **Python**: 3.11 or higher
- **MongoDB**: 7.0 or higher
- **Docker**: 24.0+ (for containerized deployment)
- **Kubernetes**: 1.28+ (for K8s deployment)
- **kubectl**: Latest version (for K8s management)

### Network Requirements

- MongoDB: Port 27017
- CMDB API: Port 8000
- Splunk HEC (optional): Port 8088

---

## Local Development

### 1. Install Dependencies

```bash
cd cmdb
pip install -r requirements.txt
```

### 2. Start MongoDB Locally

```bash
# Using Docker
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=changeme \
  mongo:7.0

# Or install MongoDB natively
# https://www.mongodb.com/docs/manual/installation/
```

### 3. Configure Environment

```bash
cp .env.example .env

# Edit .env with your settings
vi .env
```

Required environment variables:

```bash
MONGODB_URI=mongodb://admin:changeme@localhost:27017/cmdb?authSource=admin
CMDB_DATABASE=cmdb
CMDB_API_KEY=your-secure-api-key-here
LOG_LEVEL=info
ENVIRONMENT=development
```

### 4. Run the API

```bash
# Development mode (auto-reload)
python3 api.py

# Or using uvicorn directly
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/api/docs
```

### 6. Run Examples

```bash
# CMDB basic usage
python3 examples/example_usage.py

# ITSI integration
python3 examples/itsi_integration_example.py
```

### 7. Run Tests

```bash
# MongoDB client tests
cd tests
python3 test_mongodb_client.py

# API tests (requires running API)
python3 test_api_restful.py
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
cd cmdb
docker build -t suhlabs/cmdb-api:1.0.0 .
```

### 2. Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f cmdb-api

# Stop services
docker-compose down
```

Docker Compose includes:

- **MongoDB**: Database with persistent volume
- **CMDB API**: FastAPI application (3 replicas)
- **Mongo Express** (dev only): Web UI for MongoDB

### 3. Access Services

```bash
# CMDB API
curl http://localhost:8000/health

# Swagger UI
open http://localhost:8000/api/docs

# Mongo Express (dev only)
open http://localhost:8081
```

### 4. Initialize Database

```bash
# The init-mongo.js script runs automatically on first start
# To manually initialize:
docker exec -i mongodb mongosh -u admin -p changeme --authenticationDatabase admin < init-mongo.js
```

### 5. Production Deployment

For production, remove Mongo Express and update secrets:

```bash
# Edit docker-compose.yml
# Remove mongo-express service
# Update MONGO_INITDB_ROOT_PASSWORD
# Update CMDB_API_KEY

# Rebuild
docker-compose up -d --build
```

---

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Create Secrets

**IMPORTANT**: Generate secure passwords before deployment!

```bash
# Generate secure password
MONGO_PASSWORD=$(openssl rand -base64 32)
API_KEY=$(openssl rand -base64 32)

# Create MongoDB secret
kubectl create secret generic mongodb-secret \
  --from-literal=username=admin \
  --from-literal=password=$MONGO_PASSWORD \
  -n cmdb

# Create CMDB secret
kubectl create secret generic cmdb-secret \
  --from-literal=mongodb-uri="mongodb://admin:$MONGO_PASSWORD@mongodb:27017/cmdb?authSource=admin" \
  --from-literal=api-key=$API_KEY \
  -n cmdb

# Save API key for later use
echo "CMDB_API_KEY=$API_KEY" > .api_key.txt
chmod 600 .api_key.txt
```

### 3. Deploy MongoDB

```bash
# Create ConfigMap for init script
kubectl create configmap mongodb-init-script \
  --from-file=init-mongo.js \
  -n cmdb

# Deploy MongoDB StatefulSet
kubectl apply -f k8s/mongodb-statefulset.yaml

# Verify deployment
kubectl get statefulsets -n cmdb
kubectl get pods -n cmdb -l app=mongodb

# Check logs
kubectl logs -n cmdb mongodb-0 -f
```

### 4. Deploy CMDB API

```bash
# Deploy API
kubectl apply -f k8s/cmdb-api-deployment.yaml

# Verify deployment
kubectl get deployments -n cmdb
kubectl get pods -n cmdb -l app=cmdb-api

# Check logs
kubectl logs -n cmdb -l app=cmdb-api -f
```

### 5. Verify Services

```bash
# Check all resources
kubectl get all -n cmdb

# Test API health
kubectl port-forward -n cmdb svc/cmdb-api 8000:80

# In another terminal
curl http://localhost:8000/health
```

### 6. Create Ingress (Optional)

```yaml
# cmdb-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cmdb-ingress
  namespace: cmdb
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - cmdb.suhlabs.com
    secretName: cmdb-tls
  rules:
  - host: cmdb.suhlabs.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cmdb-api
            port:
              number: 80
```

```bash
kubectl apply -f cmdb-ingress.yaml
```

### 7. Scaling

```bash
# Scale API replicas
kubectl scale deployment cmdb-api --replicas=5 -n cmdb

# Horizontal Pod Autoscaler (HPA)
kubectl autoscale deployment cmdb-api \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n cmdb
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_URI` | MongoDB connection string | - | Yes |
| `CMDB_DATABASE` | Database name | `cmdb` | Yes |
| `CMDB_API_KEY` | API authentication key | - | Yes |
| `LOG_LEVEL` | Logging level | `info` | No |
| `ENVIRONMENT` | Environment name | `production` | No |
| `SPLUNK_HEC_URL` | Splunk HEC endpoint | - | No |
| `SPLUNK_HEC_TOKEN` | Splunk HEC token | - | No |

### MongoDB Configuration

**Collections Created:**

- `configuration_items`: CMDB CIs
- `baselines`: Configuration baselines (all types)
- `change_requests`: Change requests with tit-for-tat scoring
- `drift_reports`: Configuration drift reports
- `itsi_services`: ITSI services
- `itsi_kpis`: ITSI key performance indicators
- `itsi_entities`: ITSI entities
- `itsi_events`: Events for Splunk ingestion

**Indexes:**

- `configuration_items`: `ci_id` (unique), `ci_type`, `environment`, `owner`
- `baselines`: `baseline_id` (unique), `ci_id`, `status`
- `change_requests`: `cr_id` (unique), `affected_cis`
- `drift_reports`: `ci_id`, `detected_at`
- `itsi_services`: `service_id` (unique)
- `itsi_kpis`: `kpi_id` (unique), `service_id`
- `itsi_entities`: `entity_id` (unique), `cmdb_ci_id`
- `itsi_events`: `ingested`, `created_at`

### API Authentication

All write operations require API key authentication:

```bash
# Using cURL
curl -X POST http://localhost:8000/api/v1/ci \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d @ci_data.json

# Using Python requests
import requests

headers = {
    "X-API-Key": "your-api-key-here",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8000/api/v1/ci",
    headers=headers,
    json=ci_data
)
```

---

## Monitoring and Health Checks

### Health Endpoint

```bash
# Basic health check
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-19T12:00:00Z"
}
```

### Kubernetes Probes

The deployment includes:

**Liveness Probe:**
- Path: `/health`
- Initial delay: 30 seconds
- Period: 10 seconds

**Readiness Probe:**
- Path: `/health`
- Initial delay: 5 seconds
- Period: 10 seconds

### Metrics

Get CMDB statistics:

```bash
curl http://localhost:8000/api/v1/statistics

# Response includes:
# - total_cis
# - total_baselines
# - total_change_requests
# - total_drift_reports
# - cis_by_type
# - cis_by_environment
# - baselines_by_status
# - drift_by_severity
```

### Logs

**Docker Compose:**

```bash
docker-compose logs -f cmdb-api
docker-compose logs -f mongodb
```

**Kubernetes:**

```bash
# API logs
kubectl logs -n cmdb -l app=cmdb-api -f

# MongoDB logs
kubectl logs -n cmdb mongodb-0 -f

# All logs
kubectl logs -n cmdb --all-containers=true -f
```

---

## Backup and Recovery

### MongoDB Backup

**Docker:**

```bash
# Backup
docker exec mongodb mongodump \
  -u admin \
  -p changeme \
  --authenticationDatabase admin \
  --db cmdb \
  --out /backup

# Copy backup from container
docker cp mongodb:/backup ./cmdb-backup-$(date +%Y%m%d)
```

**Kubernetes:**

```bash
# Backup
kubectl exec -n cmdb mongodb-0 -- mongodump \
  -u admin \
  -p $MONGO_PASSWORD \
  --authenticationDatabase admin \
  --db cmdb \
  --archive > cmdb-backup-$(date +%Y%m%d).archive

# Automated backup (CronJob)
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mongodb-backup
  namespace: cmdb
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: mongo:7.0
            command:
            - /bin/sh
            - -c
            - mongodump --uri=$MONGODB_URI --archive=/backup/cmdb-$(date +%Y%m%d).archive
            env:
            - name: MONGODB_URI
              valueFrom:
                secretKeyRef:
                  name: cmdb-secret
                  key: mongodb-uri
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: mongodb-backup-pvc
          restartPolicy: OnFailure
```

### MongoDB Restore

```bash
# Docker
docker exec -i mongodb mongorestore \
  -u admin \
  -p changeme \
  --authenticationDatabase admin \
  --archive < cmdb-backup-20251019.archive

# Kubernetes
kubectl exec -i -n cmdb mongodb-0 -- mongorestore \
  -u admin \
  -p $MONGO_PASSWORD \
  --authenticationDatabase admin \
  --archive < cmdb-backup-20251019.archive
```

---

## Troubleshooting

### API Won't Start

**Check MongoDB connection:**

```bash
# Docker
docker exec -it mongodb mongosh -u admin -p changeme --authenticationDatabase admin

# Kubernetes
kubectl exec -it -n cmdb mongodb-0 -- mongosh -u admin -p $MONGO_PASSWORD --authenticationDatabase admin
```

**Check logs:**

```bash
# Docker
docker-compose logs cmdb-api

# Kubernetes
kubectl logs -n cmdb -l app=cmdb-api
```

### Database Connection Issues

**Verify connection string:**

```bash
# Test from API container
kubectl exec -it -n cmdb <cmdb-api-pod> -- python3 -c "
from pymongo import MongoClient
import os
client = MongoClient(os.getenv('MONGODB_URI'))
print(client.server_info())
"
```

### Permission Errors

**Check file permissions (Docker):**

```bash
# Ensure cmdb user owns files
docker exec -it <container-id> ls -la /app
```

### Pod Crashes (Kubernetes)

**Check events:**

```bash
kubectl describe pod -n cmdb <pod-name>
kubectl get events -n cmdb --sort-by='.lastTimestamp'
```

**Check resource limits:**

```bash
kubectl top pods -n cmdb
kubectl describe node <node-name>
```

### ITSI Events Not Ingesting

**Check pending events:**

```bash
curl http://localhost:8000/api/v1/itsi/events?limit=10
```

**Manually mark as ingested:**

```bash
curl -X POST http://localhost:8000/api/v1/itsi/events/mark_ingested \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '["event-id-1", "event-id-2"]'
```

---

## Production Checklist

- [ ] Generate secure MongoDB password (32+ characters)
- [ ] Generate secure API key (32+ characters)
- [ ] Store secrets in secure vault (e.g., HashiCorp Vault, AWS Secrets Manager)
- [ ] Enable TLS for MongoDB connections
- [ ] Configure Ingress with TLS/SSL certificates
- [ ] Set up automated backups (daily minimum)
- [ ] Configure log aggregation (Splunk, ELK, etc.)
- [ ] Set up monitoring and alerting (Prometheus, Grafana)
- [ ] Enable horizontal pod autoscaling
- [ ] Configure network policies
- [ ] Set resource requests and limits appropriately
- [ ] Test disaster recovery procedures
- [ ] Document runbooks for common operations
- [ ] Set up CI/CD pipeline for updates

---

## Support

For issues or questions:

- **Internal**: governance-team@suhlabs.com
- **Documentation**: See `docs/CMDB-ARCHITECTURE.md`
- **Examples**: See `cmdb/examples/`
- **Tests**: See `cmdb/tests/`
