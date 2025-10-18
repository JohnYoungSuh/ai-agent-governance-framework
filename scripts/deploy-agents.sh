#!/bin/bash
# Deploy All AI Agents
# AI Agent Governance Framework

set -e

ENVIRONMENT=${1:-dev}
NAMESPACE="ai-agents-${ENVIRONMENT}"

echo "=========================================="
echo "AI Agent Governance Framework"
echo "Agent Deployment to $ENVIRONMENT"
echo "=========================================="

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
