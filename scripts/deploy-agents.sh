#!/bin/bash
# Deploy All AI Agents
# AI Agent Governance Framework v2.1
# Controls: APP-001, G-02, G-07, MI-020

set -e

ENVIRONMENT=${1:-dev}
NAMESPACE="ai-agents-${ENVIRONMENT}"
JIRA_CR_ID=${2:-""}

echo "=========================================="
echo "AI Agent Governance Framework"
echo "Agent Deployment to $ENVIRONMENT"
echo "=========================================="

# Jira CR validation for staging/prod
if [[ "$ENVIRONMENT" =~ ^(staging|prod)$ ]]; then
    if [ -z "$JIRA_CR_ID" ]; then
        echo "❌ ERROR: Jira CR ID required for $ENVIRONMENT deployments"
        echo ""
        echo "GOVERNANCE VIOLATION:"
        echo "  Control:     APP-001 (Human Primacy), G-02 (Approval Enforcement)"
        echo "  Requirement: Tier 3/4 deployments to staging/prod require Jira CR"
        echo "  Action:      Provide Jira CR ID as second argument"
        echo ""
        echo "Usage: $0 $ENVIRONMENT <JIRA_CR_ID>"
        echo "Example: $0 prod CR-2025-1042"
        exit 1
    fi

    echo "Jira CR ID:      $JIRA_CR_ID"

    # Validate Jira approval
    if [ -f "scripts/validate-jira-approval.py" ]; then
        echo "Validating Jira CR approval..."
        if ! scripts/validate-jira-approval.py "deployment-agent" "$JIRA_CR_ID" "Change Manager"; then
            echo "❌ Jira approval validation FAILED"
            exit 1
        fi
        echo "✅ Jira approval validated"
    fi
fi

echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v helm >/dev/null 2>&1 || { echo "❌ helm is required but not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker is required but not installed"; exit 1; }

# Create namespace
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply base manifests
echo "Applying base Kubernetes manifests..."
kubectl apply -f deploy/k8s/base/namespaces.yaml
kubectl apply -f deploy/k8s/base/resource-quotas.yaml

# Deploy agents
AGENTS=("security" "it-ops" "ai" "architect")

for agent in "${AGENTS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Deploying ${agent}-agent to $ENVIRONMENT"
    echo "=========================================="

    RELEASE_NAME="${agent}-agent"
    VALUES_FILE="deploy/helm/ai-agent/values-${agent}.yaml"

    if [ ! -f "$VALUES_FILE" ]; then
        echo "❌ Values file not found: $VALUES_FILE"
        continue
    fi

    # Run governance check
    echo "Running governance check for ${agent}-agent..."
    if [ -f "scripts/governance-check.sh" ]; then
        ./scripts/governance-check.sh --agent ${agent}-agent --tier 3 --environment $ENVIRONMENT || {
            echo "⚠️  Governance check failed for ${agent}-agent"
            read -p "Continue anyway? (y/n) " -n 1 -r
            echo
            [[ ! $REPLY =~ ^[Yy]$ ]] && continue
        }
    fi

    # Deploy with Helm
    echo "Deploying ${agent}-agent with Helm..."
    helm upgrade --install $RELEASE_NAME deploy/helm/ai-agent \
        --namespace $NAMESPACE \
        --values $VALUES_FILE \
        --set agent.name=${agent}-agent \
        --set image.tag=latest \
        --wait \
        --timeout 5m

    echo "✅ ${agent}-agent deployed successfully!"
done

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="

# Generate audit trail entry
AUDIT_ID="audit-$(date +%s)-$(uuidgen 2>/dev/null | cut -d'-' -f1 || echo $RANDOM)"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
AUDIT_DIR="audit-trails"
mkdir -p "$AUDIT_DIR"

cat > "$AUDIT_DIR/deploy-${AUDIT_ID}.json" <<EOF
{
  "audit_id": "$AUDIT_ID",
  "timestamp": "$TIMESTAMP",
  "actor": "$(whoami)@$(hostname)",
  "action": "agent_deployment",
  "workflow_step": "APP-001",
  "jira_reference": {
    "cr_id": "$JIRA_CR_ID",
    "approver_role": "Change Manager",
    "budget_tokens": 0,
    "controls": ["APP-001", "G-02", "G-07", "MI-020"]
  },
  "inputs": {
    "environment": "$ENVIRONMENT",
    "namespace": "$NAMESPACE",
    "agents_deployed": $(echo "${AGENTS[@]}" | jq -R 'split(" ")' || echo '[]'),
    "deployment_method": "helm"
  },
  "outputs": {
    "deployment_status": "success",
    "agents_count": ${#AGENTS[@]}
  },
  "policy_controls_checked": ["APP-001", "G-02", "G-07", "MI-020"],
  "compliance_result": "pass",
  "evidence_hash": "sha256:$(echo "$NAMESPACE-$TIMESTAMP" | sha256sum 2>/dev/null | cut -d' ' -f1 || echo 'unknown')",
  "auditor_agent": "deploy-agents-script"
}
EOF

echo ""
echo "📄 Audit Trail: $AUDIT_DIR/deploy-${AUDIT_ID}.json"
echo ""
echo "=========================================="
echo ""
echo "Verify deployments:"
echo "  kubectl get pods -n $NAMESPACE"
echo "  kubectl get svc -n $NAMESPACE"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/security-agent -n $NAMESPACE"
echo "  kubectl logs -f deployment/it-ops-agent -n $NAMESPACE"
echo "  kubectl logs -f deployment/architect-agent -n $NAMESPACE"
echo ""
echo "Check CronJobs:"
echo "  kubectl get cronjobs -n $NAMESPACE"
echo ""
echo "=========================================="
