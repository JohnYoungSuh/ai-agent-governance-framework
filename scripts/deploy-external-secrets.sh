#!/bin/bash
# Deploy External Secrets Operator
# AI Agent Governance Framework

set -e

NAMESPACE="external-secrets-system"
RELEASE_NAME="external-secrets"

echo "=========================================="
echo "AI Agent Governance Framework"
echo "External Secrets Operator Deployment"
echo "=========================================="

# Check prerequisites
echo "Checking prerequisites..."
command -v helm >/dev/null 2>&1 || { echo "❌ helm is required but not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed"; exit 1; }

# Create namespace
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Add Helm repository
echo "Adding External Secrets Helm repository..."
helm repo add external-secrets https://charts.external-secrets.io
helm repo update

# Install External Secrets Operator
echo "Installing External Secrets Operator..."
helm upgrade --install $RELEASE_NAME external-secrets/external-secrets \
  --namespace $NAMESPACE \
  --set installCRDs=true \
  --wait

# Wait for pods to be ready
echo "Waiting for External Secrets pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=external-secrets -n $NAMESPACE --timeout=300s

# Apply SecretStore and ExternalSecrets
echo "Applying SecretStore and ExternalSecret configurations..."
echo "⚠️  NOTE: Update AWS account ID in deploy/k8s/base/external-secrets.yaml before applying"

read -p "Have you updated the AWS account ID? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    kubectl apply -f deploy/k8s/base/external-secrets.yaml
    echo "✅ External Secrets configured successfully!"
else
    echo "⚠️  Skipping ExternalSecret creation. Apply manually after updating account ID:"
    echo "   kubectl apply -f deploy/k8s/base/external-secrets.yaml"
fi

echo ""
echo "✅ External Secrets Operator deployed successfully!"
echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Create secrets in AWS Secrets Manager:"
echo "   - ai-agents/prod/security-agent"
echo "   - ai-agents/prod/it-ops-agent"
echo "   - ai-agents/prod/ai-agent"
echo "   - ai-agents/prod/architect-agent"
echo "   - ai-agents/prod/shared"
echo ""
echo "2. Configure IRSA (IAM Roles for Service Accounts) for EKS:"
echo "   eksctl create iamserviceaccount \\"
echo "     --name external-secrets-sa \\"
echo "     --namespace ai-agents-prod \\"
echo "     --cluster YOUR_CLUSTER \\"
echo "     --attach-policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite \\"
echo "     --approve"
echo ""
echo "3. Verify secrets are synced:"
echo "   kubectl get externalsecrets -n ai-agents-prod"
echo "   kubectl get secrets -n ai-agents-prod"
echo ""
echo "=========================================="
