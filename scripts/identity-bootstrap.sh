#!/usr/bin/env bash
#
# Identity Bootstrapping — AI Agent Governance Framework
#
# Sets up K8s namespaces, ServiceAccounts, RBAC roles, and Conjur ConfigMaps
# required for ZT secretless brokerage and token volume projection.
#
# Standard: NIST SP 800-207 Zero Trust Architecture + Pod Security Standards (PSS)

set -euo pipefail

NAMESPACE_PROD="ai-agents-prod"
NAMESPACE_DEV="ai-agents-dev"
NAMESPACE_INFRA="ai-agents-infra"

echo "=== Establishing Zero Trust Namespaces ==="
for ns in "${NAMESPACE_PROD}" "${NAMESPACE_DEV}" "${NAMESPACE_INFRA}"; do
  echo "Ensuring namespace: ${ns}"
  kubectl create namespace "${ns}" --dry-run=client -o yaml | kubectl apply -f -
  
  # Apply Pod Security Standards (PSS) Restricted Label (SC-39 / NIST)
  echo "Applying Restricted Pod Security Standards to ${ns}"
  kubectl label namespace "${ns}" --overwrite \
    pod-security.kubernetes.io/enforce=restricted \
    pod-security.kubernetes.io/enforce-version=latest \
    pod-security.kubernetes.io/warn=restricted \
    pod-security.kubernetes.io/warn-version=latest
done

echo "=== Creating Conjur SSL Certificate ConfigMap (Dev/Prod) ==="
# Dummy cert mapping for demonstration/bootstrapping, actual config would map real cert
for ns in "${NAMESPACE_DEV}" "${NAMESPACE_PROD}"; do
  kubectl create configmap conjur-cert \
    --namespace="${ns}" \
    --from-literal=ssl-certificate="---BEGIN CERTIFICATE---
MIIFBDCCAuygAwIBAgIRAP6P1d2g+q03FvL4V2xYw8AwDQYJKoZIhvcNAQELBQAw
...
---END CERTIFICATE---" \
    --dry-run=client -o yaml | kubectl apply -f -
done

echo "=== Deploying ServiceAccounts & RBAC Tiers ==="
# Map service accounts for each agent role: security, it-ops, ai, architect
for agent in "security-agent" "it-ops-agent" "ai-agent" "architect-agent" "governance-router"; do
  echo "Deploying ServiceAccount: ${agent} in ${NAMESPACE_PROD}"
  
  # Automount disabled - explicitly projected token volume required (Guardrail #8)
  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ${agent}
  namespace: ${NAMESPACE_PROD}
  labels:
    app.kubernetes.io/name: ${agent}
    governance.ai/role: agent
automountServiceAccountToken: false
EOF

  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ${agent}
  namespace: ${NAMESPACE_DEV}
  labels:
    app.kubernetes.io/name: ${agent}
    governance.ai/role: agent
automountServiceAccountToken: false
EOF
done

echo "=== Applying RBAC Bindings for Agent Tiers (Least Privilege AC-6) ==="
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ai-agent-base-reader
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ai-agent-tier3-operator
rules:
  - apiGroups: [""]
    resources: ["pods/exec", "pods", "services", "configmaps"]
    verbs: ["create", "get", "list", "watch", "update", "patch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "statefulsets"]
    verbs: ["get", "list", "watch", "update", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: ai-agent-tier4-architect
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
EOF

# Bindings for Prod
for ns in "${NAMESPACE_PROD}" "${NAMESPACE_DEV}"; do
  # Tier 1/2 bases: base reader
  for agent in "security-agent" "ai-agent"; do
    cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ${agent}-base-binding
  namespace: ${ns}
subjects:
  - kind: ServiceAccount
    name: ${agent}
    namespace: ${ns}
roleRef:
  kind: ClusterRole
  name: ai-agent-base-reader
  apiGroup: rbac.authorization.k8s.io
EOF
  done

  # Tier 3: it-ops has operator permissions
  cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: it-ops-agent-operator-binding
  namespace: ${ns}
subjects:
  - kind: ServiceAccount
    name: it-ops-agent
    namespace: ${ns}
roleRef:
  kind: ClusterRole
  name: ai-agent-tier3-operator
  apiGroup: rbac.authorization.k8s.io
EOF

  # Tier 4: architect has full permissions (subject to GPIS check + PA approvals)
  cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: architect-agent-architect-binding
  namespace: ${ns}
subjects:
  - kind: ServiceAccount
    name: architect-agent
    namespace: ${ns}
roleRef:
  kind: ClusterRole
  name: ai-agent-tier4-architect
  apiGroup: rbac.authorization.k8s.io
EOF
done

echo "=== Creating Conjur Authenticator ConfigMap ==="
# Map the authentication endpoint configuration for authn-k8s
for ns in "${NAMESPACE_DEV}" "${NAMESPACE_PROD}"; do
  cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: conjur-authenticator-config
  namespace: ${ns}
data:
  conjur_url: "https://conjur.ai-agents-infra.svc.cluster.local/authn-k8s/dev"
  conjur_account: "dev"
  conjur_cluster_id: "home-cluster-devsecops"
EOF
done

echo "=== Verifying Bootstrapping Configuration (NIST AC-6/SC-39 Validation) ==="
echo "Namespaces check:"
kubectl get namespaces -l pod-security.kubernetes.io/enforce=restricted

echo "ServiceAccounts check:"
kubectl get sa --namespace="${NAMESPACE_PROD}"

echo "Identity Bootstrapping Complete. Ready for sidecar verification."
