#!/bin/bash
# Deploy Monitoring Stack (Prometheus + Grafana)
# AI Agent Governance Framework

set -e

NAMESPACE="ai-agents-monitoring"
RELEASE_NAME="prometheus"

echo "=========================================="
echo "AI Agent Governance Framework"
echo "Monitoring Stack Deployment"
echo "=========================================="

# Check prerequisites
echo "Checking prerequisites..."
command -v helm >/dev/null 2>&1 || { echo "❌ helm is required but not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl is required but not installed"; exit 1; }

# Create namespace
echo "Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Add Helm repositories
echo "Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Prometheus Operator
echo "Installing Prometheus Operator..."
helm upgrade --install $RELEASE_NAME prometheus-community/kube-prometheus-stack \
  --namespace $NAMESPACE \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set grafana.enabled=true \
  --set grafana.adminPassword=admin \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.size=10Gi \
  --wait

# Apply custom PrometheusRules
echo "Applying custom alert rules..."
kubectl apply -f deploy/k8s/base/monitoring-stack.yaml

# Wait for pods to be ready
echo "Waiting for monitoring pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n $NAMESPACE --timeout=300s

# Get Grafana password
GRAFANA_PASSWORD=$(kubectl get secret -n $NAMESPACE prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode)

echo ""
echo "✅ Monitoring stack deployed successfully!"
echo ""
echo "=========================================="
echo "Access Information"
echo "=========================================="
echo ""
echo "Prometheus:"
echo "  kubectl port-forward -n $NAMESPACE svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "  Then open: http://localhost:9090"
echo ""
echo "Grafana:"
echo "  kubectl port-forward -n $NAMESPACE svc/prometheus-grafana 3000:80"
echo "  Then open: http://localhost:3000"
echo "  Username: admin"
echo "  Password: $GRAFANA_PASSWORD"
echo ""
echo "AlertManager:"
echo "  kubectl port-forward -n $NAMESPACE svc/prometheus-kube-prometheus-alertmanager 9093:9093"
echo "  Then open: http://localhost:9093"
echo ""
echo "=========================================="
