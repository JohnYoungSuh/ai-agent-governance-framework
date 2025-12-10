# [DEPRECATED] GPIS Implementation Guide
> [!WARNING]
> **This document has been superseded by [PATENT-DISCLOSURE.md](../docs/PATENT-DISCLOSURE.md).**
> Please refer to the Patent Disclosure for the authoritative technical specification.

# GPIS Quick Implementation Guide

**Target Audience:** Engineering team implementing GPIS  
**Timeline:** 12 weeks to production  
**Prerequisites:** Python 3.9+, Docker, Kubernetes, AWS/Azure account

---

## Week 1-4: Phase 1 - Core GPIS Service

### Step 1: Set Up Project Structure

```bash
cd ~/projects/suhlabs/ai-agent-governance-framework
mkdir -p gpis/{api,policy_engine,decision_ledger,identity,budget,escalation}
mkdir -p gpis/tests
```

### Step 2: Create GPIS API Service (FastAPI)

**File:** `gpis/api/main.py`

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime
from typing import Optional

app = FastAPI(title="Governance Policy Inquiry Service (GPIS)")
security = HTTPBearer()

# Request/Response Models
class GPISRequest(BaseModel):
    message_id: str
    timestamp: str
    source_namespace: str
    source_agent_identity: str
    destination_namespace: str
    destination_resource: str
    action: str
    action_parameters: dict
    justification: str
    cost_center: str
    project_code: str
    estimated_cost: float
    dry_run: bool = False
    trace_id: Optional[str] = None

class GPISResponse(BaseModel):
    decision_id: str
    timestamp: str
    request_id: str
    decision: str  # AUTO-APPROVE, HUMAN-REQUIRED, DENY
    tier: int  # 0, 1, 2, 3
    justification: str
    policy_citation: dict
    compliance_metadata: dict
    next_steps: str
    audit_log_id: str
    escalation_id: Optional[str] = None
    expires_at: str

# Identity validation
async def validate_identity(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and extract agent identity"""
    try:
        token = credentials.credentials
        # TODO: Verify JWT signature with public key
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.post("/evaluate", response_model=GPISResponse)
async def evaluate_request(request: GPISRequest, identity: dict = Depends(validate_identity)):
    """Main GPIS evaluation endpoint"""
    
    decision_id = f"dec-{datetime.now().strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:8]}"
    
    # 1. Validate namespace
    if request.source_namespace != identity.get("namespace"):
        return GPISResponse(
            decision_id=decision_id,
            timestamp=datetime.now().isoformat(),
            request_id=request.message_id,
            decision="DENY",
            tier=3,
            justification=f"Namespace mismatch: claimed={request.source_namespace}, actual={identity.get('namespace')}",
            policy_citation={
                "policy_id": "unified-governance-v3",
                "policy_version": "3.0.0",
                "rule_applied": "namespace_isolation"
            },
            compliance_metadata={
                "cost_center": request.cost_center,
                "project_code": request.project_code,
                "trace_id": request.trace_id
            },
            next_steps="Action denied due to namespace violation. Contact governance team.",
            audit_log_id=f"audit-{decision_id}",
            expires_at=datetime.now().isoformat()
        )
    
    # 2. Classify action tier
    tier = classify_action_tier(request, identity)
    
    # 3. Make decision
    if tier == 0 or tier == 1:
        decision = "AUTO-APPROVE"
        justification = f"Action '{request.action}' is within agent privileges and quotas"
        next_steps = "Proceed with action. Logged to Decision Ledger for audit."
        escalation_id = None
    elif tier == 2:
        decision = "HUMAN-REQUIRED"
        escalation_id = f"ESC-{datetime.now().year}-{uuid.uuid4().hex[:6]}"
        justification = f"Action '{request.action}' requires human approval"
        next_steps = f"Escalation {escalation_id} created. You will be notified when approved."
    else:  # tier == 3
        decision = "DENY"
        justification = f"Action '{request.action}' is prohibited by policy"
        next_steps = "Action denied. Contact governance team if you believe this is an error."
        escalation_id = None
    
    # 4. Log to Decision Ledger (async)
    audit_log_id = await log_to_decision_ledger(decision_id, request, decision, tier)
    
    return GPISResponse(
        decision_id=decision_id,
        timestamp=datetime.now().isoformat(),
        request_id=request.message_id,
        decision=decision,
        tier=tier,
        justification=justification,
        policy_citation={
            "policy_id": "unified-governance-v3",
            "policy_version": "3.0.0",
            "rule_applied": f"action_tiers.tier_{tier}"
        },
        compliance_metadata={
            "cost_center": request.cost_center,
            "project_code": request.project_code,
            "estimated_cost": request.estimated_cost,
            "trace_id": request.trace_id
        },
        next_steps=next_steps,
        audit_log_id=audit_log_id,
        escalation_id=escalation_id,
        expires_at=(datetime.now() + timedelta(hours=4)).isoformat()
    )

def classify_action_tier(request: GPISRequest, identity: dict) -> int:
    """Classify action into Tier 0-3"""
    
    # Tier 3: Prohibited actions
    prohibited_actions = [
        "credential_sharing",
        "audit_log_deletion",
        "policy_bypass",
        "rm_rf_root"
    ]
    if request.action in prohibited_actions:
        return 3
    
    # Tier 2: Cross-namespace operations
    if request.source_namespace != request.destination_namespace:
        return 2
    
    # Tier 2: Budget overage
    # TODO: Check real-time budget
    
    # Tier 1: Routine operations within quota
    tier_1_actions = [
        "scale_deployment",
        "create_resource",
        "update_resource"
    ]
    if request.action in tier_1_actions:
        return 1
    
    # Tier 0: Read-only operations
    tier_0_actions = [
        "read_data",
        "list_resources",
        "get_status"
    ]
    if request.action in tier_0_actions:
        return 0
    
    # Default: Escalate if uncertain
    return 2

async def log_to_decision_ledger(decision_id: str, request: GPISRequest, decision: str, tier: int) -> str:
    """Log decision to immutable Decision Ledger"""
    
    audit_log_id = f"audit-{decision_id}"
    
    ledger_entry = {
        "decision_id": decision_id,
        "timestamp": datetime.now().isoformat(),
        "agent_identity": request.source_agent_identity,
        "namespace": request.source_namespace,
        "action": request.action,
        "action_tier": tier,
        "decision": decision,
        "policy_id": "unified-governance-v3",
        "policy_version": "3.0.0",
        "justification": f"Tier {tier} decision",
        "cost_center": request.cost_center,
        "project_code": request.project_code,
        "estimated_cost": request.estimated_cost,
        "trace_id": request.trace_id,
        "resource_affected": request.destination_resource
    }
    
    # TODO: Write to S3 with Object Lock
    # For now, just log to stdout
    print(f"DECISION_LEDGER: {ledger_entry}")
    
    return audit_log_id

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "gpis", "version": "1.0.0"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # TODO: Implement Prometheus metrics
    return {"metrics": "TODO"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Step 3: Create Dockerfile

**File:** `gpis/Dockerfile`

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY api/ ./api/
COPY policy_engine/ ./policy_engine/
COPY decision_ledger/ ./decision_ledger/

# Expose ports
EXPOSE 8080 9090

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**File:** `gpis/requirements.txt`

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-jose[cryptography]==3.3.0
boto3==1.29.0
prometheus-client==0.19.0
```

### Step 4: Deploy to Kubernetes

**File:** `deploy/kubernetes/gpis-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpis
  namespace: governance
  labels:
    app: gpis
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gpis
  template:
    metadata:
      labels:
        app: gpis
        version: v1.0.0
    spec:
      containers:
      - name: gpis
        image: governance.ai/gpis:v1.0.0
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: POLICY_REPO_URL
          value: "https://github.com/org/governance-policies.git"
        - name: DECISION_LEDGER_BUCKET
          value: "s3://governance-decision-ledger"
        - name: JWT_PUBLIC_KEY
          valueFrom:
            secretKeyRef:
              name: gpis-secrets
              key: jwt-public-key
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: gpis
  namespace: governance
spec:
  selector:
    app: gpis
  ports:
  - name: http
    port: 80
    targetPort: 8080
  - name: metrics
    port: 9090
    targetPort: 9090
  type: LoadBalancer
```

### Step 5: Test GPIS API

```bash
# Build and deploy
cd gpis
docker build -t gpis:v1.0.0 .
kubectl apply -f ../deploy/kubernetes/gpis-deployment.yaml

# Test health endpoint
curl http://gpis.governance/health

# Test evaluation endpoint (requires JWT token)
curl -X POST http://gpis.governance/evaluate \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg-123",
    "timestamp": "2025-11-22T19:00:00Z",
    "source_namespace": "team-alpha",
    "source_agent_identity": "team-alpha-deploy-001",
    "destination_namespace": "team-alpha",
    "destination_resource": "deployment/web-app",
    "action": "scale_deployment",
    "action_parameters": {"replicas": 5},
    "justification": "Traffic spike",
    "cost_center": "CC-12345",
    "project_code": "PROJ-ALPHA-2025",
    "estimated_cost": 15.50,
    "dry_run": false
  }'
```

---

## Week 5-6: Phase 2 - Human Escalation

### Step 1: Implement Escalation Router

**File:** `gpis/escalation/router.py`

```python
import requests
from typing import Dict

class EscalationRouter:
    """Routes Tier 2 escalations to appropriate approvers"""
    
    def __init__(self, jira_url: str, jira_token: str, slack_webhook: str):
        self.jira_url = jira_url
        self.jira_token = jira_token
        self.slack_webhook = slack_webhook
    
    async def create_escalation(self, escalation_id: str, request: dict, reason: str) -> dict:
        """Create escalation in Jira and notify via Slack"""
        
        # Determine routing based on reason
        if "budget" in reason.lower():
            assignee = "finops-team"
            priority = "High"
        elif "security" in reason.lower():
            assignee = "security-team"
            priority = "Critical"
        else:
            assignee = "governance-team"
            priority = "Medium"
        
        # Create Jira ticket
        jira_ticket = self._create_jira_ticket(
            escalation_id=escalation_id,
            assignee=assignee,
            priority=priority,
            request=request,
            reason=reason
        )
        
        # Send Slack notification
        self._send_slack_notification(
            escalation_id=escalation_id,
            assignee=assignee,
            jira_ticket=jira_ticket,
            request=request
        )
        
        return {
            "escalation_id": escalation_id,
            "jira_ticket": jira_ticket,
            "assignee": assignee,
            "sla_hours": 4,
            "approval_url": f"{self.jira_url}/browse/{jira_ticket}"
        }
    
    def _create_jira_ticket(self, escalation_id: str, assignee: str, priority: str, request: dict, reason: str) -> str:
        """Create Jira ticket for escalation"""
        
        payload = {
            "fields": {
                "project": {"key": "GOV"},
                "summary": f"GPIS Escalation: {escalation_id}",
                "description": f"""
                Agent: {request['source_agent_identity']}
                Action: {request['action']}
                Reason: {reason}
                Justification: {request['justification']}
                Cost: ${request['estimated_cost']}
                """,
                "issuetype": {"name": "Task"},
                "priority": {"name": priority},
                "assignee": {"name": assignee}
            }
        }
        
        response = requests.post(
            f"{self.jira_url}/rest/api/2/issue",
            headers={"Authorization": f"Bearer {self.jira_token}"},
            json=payload
        )
        
        return response.json()["key"]
    
    def _send_slack_notification(self, escalation_id: str, assignee: str, jira_ticket: str, request: dict):
        """Send Slack notification"""
        
        message = {
            "text": f"🚨 GPIS Escalation: {escalation_id}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*GPIS Escalation Required*\n\nAgent: `{request['source_agent_identity']}`\nAction: `{request['action']}`\nAssignee: @{assignee}\nJira: <{self.jira_url}/browse/{jira_ticket}|{jira_ticket}>"
                    }
                }
            ]
        }
        
        requests.post(self.slack_webhook, json=message)
```

### Step 2: Integrate with GPIS API

Update `gpis/api/main.py`:

```python
from escalation.router import EscalationRouter

# Initialize escalation router
escalation_router = EscalationRouter(
    jira_url=os.getenv("JIRA_URL"),
    jira_token=os.getenv("JIRA_TOKEN"),
    slack_webhook=os.getenv("SLACK_WEBHOOK")
)

# In evaluate_request function, when tier == 2:
elif tier == 2:
    decision = "HUMAN-REQUIRED"
    escalation_id = f"ESC-{datetime.now().year}-{uuid.uuid4().hex[:6]}"
    
    # Create escalation
    escalation_details = await escalation_router.create_escalation(
        escalation_id=escalation_id,
        request=request.dict(),
        reason=justification
    )
    
    justification = f"Action '{request.action}' requires human approval"
    next_steps = f"Escalation {escalation_id} created. Jira ticket: {escalation_details['jira_ticket']}. SLA: {escalation_details['sla_hours']} hours."
```

---

## Week 7-8: Phase 3 - Advanced Features

### Step 1: Implement Safety Checks

**File:** `gpis/policy_engine/safety_checks.py`

```python
class SafetyChecker:
    """Enforce safety requirements for high-risk actions"""
    
    def check_destructive_action(self, request: dict) -> dict:
        """Check if destructive action has required safety measures"""
        
        destructive_actions = ["delete", "drop", "truncate", "rm"]
        
        if any(action in request["action"].lower() for action in destructive_actions):
            # Require dry-run evidence
            if not request.get("dry_run_evidence"):
                return {
                    "decision": "DENY",
                    "tier": 3,
                    "justification": "Destructive action requires dry-run simulation first"
                }
            
            # Require rollback plan
            if not request.get("rollback_plan"):
                return {
                    "decision": "HUMAN-REQUIRED",
                    "tier": 2,
                    "justification": "Destructive action requires rollback plan"
                }
        
        return {"decision": "PROCEED"}
    
    def check_idempotency(self, request: dict) -> dict:
        """Check if high-impact action is idempotent"""
        
        high_impact_actions = ["deploy", "migrate", "scale"]
        
        if any(action in request["action"].lower() for action in high_impact_actions):
            if not request.get("idempotent"):
                return {
                    "decision": "HUMAN-REQUIRED",
                    "tier": 2,
                    "justification": "High-impact action must be idempotent"
                }
        
        return {"decision": "PROCEED"}
```

---

## Week 9-12: Phase 4 - Production Hardening

### Step 1: Add Prometheus Metrics

**File:** `gpis/api/metrics.py`

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Metrics
gpis_requests_total = Counter('gpis_requests_total', 'Total GPIS requests', ['tier', 'decision'])
gpis_decision_latency = Histogram('gpis_decision_latency_seconds', 'GPIS decision latency', ['tier'])
gpis_autonomy_rate = Gauge('gpis_autonomy_rate', 'Autonomy rate (Tier 0+1 / Total)')
gpis_budget_utilization = Gauge('gpis_budget_utilization_percent', 'Budget utilization', ['agent_identity'])

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")
```

### Step 2: Create Grafana Dashboard

**File:** `deploy/monitoring/gpis-dashboard.json`

```json
{
  "dashboard": {
    "title": "GPIS Monitoring",
    "panels": [
      {
        "title": "Autonomy Rate",
        "targets": [
          {
            "expr": "gpis_autonomy_rate"
          }
        ],
        "type": "gauge"
      },
      {
        "title": "Decision Latency (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, gpis_decision_latency_seconds_bucket)"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Decisions by Tier",
        "targets": [
          {
            "expr": "sum by (tier) (gpis_requests_total)"
          }
        ],
        "type": "piechart"
      }
    ]
  }
}
```

---

## Testing Checklist

### Phase 1 Tests
- [ ] GPIS API responds to `/health` endpoint
- [ ] JWT authentication works
- [ ] Tier 0 decisions <50ms latency
- [ ] Tier 1 decisions <100ms latency
- [ ] Decision Ledger receives all decisions
- [ ] Namespace validation rejects mismatches

### Phase 2 Tests
- [ ] Tier 2 escalations create Jira tickets
- [ ] Slack notifications sent
- [ ] Timeout handling works (auto-deny)
- [ ] Budget overage detected
- [ ] Approval workflow completes

### Phase 3 Tests
- [ ] Tier 3 denials <50ms latency
- [ ] Destructive actions require dry-run
- [ ] Rollback plans validated
- [ ] Idempotency checks work
- [ ] mTLS enforcement active

### Phase 4 Tests
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards render
- [ ] Multi-region deployment works
- [ ] Disaster recovery tested
- [ ] ≥80% autonomy rate achieved

---

## Deployment Commands

```bash
# Phase 1: Deploy Core GPIS
kubectl apply -f deploy/kubernetes/gpis-deployment.yaml
kubectl apply -f deploy/kubernetes/gpis-service.yaml

# Phase 2: Deploy Escalation Router
kubectl apply -f deploy/kubernetes/gpis-escalation-configmap.yaml

# Phase 3: Deploy Safety Checks
kubectl apply -f deploy/kubernetes/gpis-policy-configmap.yaml

# Phase 4: Deploy Monitoring
kubectl apply -f deploy/monitoring/prometheus-config.yaml
kubectl apply -f deploy/monitoring/grafana-dashboard.yaml
```

---

## Troubleshooting

### GPIS API not responding
```bash
kubectl logs -n governance deployment/gpis
kubectl describe pod -n governance -l app=gpis
```

### Decision Ledger writes failing
```bash
# Check S3 bucket permissions
aws s3api get-bucket-versioning --bucket governance-decision-ledger
aws s3api get-object-lock-configuration --bucket governance-decision-ledger
```

### Escalations not routing
```bash
# Check Jira integration
kubectl logs -n governance deployment/gpis | grep "escalation"
# Check Slack webhook
curl -X POST $SLACK_WEBHOOK -d '{"text":"Test"}'
```

---

## Next Steps

After completing all 4 phases:

1. **Monitor autonomy rate** - Target ≥80%
2. **Review escalation patterns** - Identify policy improvements
3. **Optimize performance** - Reduce latency further
4. **Expand coverage** - Integrate more agents
5. **Continuous improvement** - Iterate based on feedback

**Congratulations!** You now have a production-ready GPIS implementing Zero Trust for AI Agents with Total Accountability.
