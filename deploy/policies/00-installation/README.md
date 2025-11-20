# Kubernetes-Native Policy Framework - Installation Guide

## Overview

This directory contains installation manifests for the policy enforcement engines:
- **Gatekeeper** (OPA) - For complex policy logic using Rego
- **Kyverno** - For simple YAML-based policies

## Prerequisites

- Kubernetes cluster version **1.25+** (for Pod Security Admission support)
- `kubectl` configured with cluster-admin access
- Cluster with at least 2 CPU and 4Gi memory available

## Installation Order

Install in this exact order:

### 1. Install Gatekeeper (OPA)

```bash
# Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.15.0/deploy/gatekeeper.yaml

# Wait for Gatekeeper to be ready
kubectl wait --for=condition=Ready pod -l control-plane=controller-manager \
  -n gatekeeper-system --timeout=120s

# Verify installation
kubectl get pods -n gatekeeper-system
kubectl get crd | grep gatekeeper
```

**Expected Output:**
```
NAME                                             READY   STATUS    RESTARTS   AGE
gatekeeper-audit-xxxxxxxxx-xxxxx                 1/1     Running   0          60s
gatekeeper-controller-manager-xxxxxxxxx-xxxxx    1/1     Running   0          60s
gatekeeper-controller-manager-xxxxxxxxx-xxxxx    1/1     Running   0          60s
```

### 2. Install Kyverno

```bash
# Install Kyverno
kubectl apply -f https://github.com/kyverno/kyverno/releases/download/v1.11.0/install.yaml

# Wait for Kyverno to be ready
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=kyverno \
  -n kyverno --timeout=120s

# Verify installation
kubectl get pods -n kyverno
kubectl get crd | grep kyverno
```

**Expected Output:**
```
NAME                                  READY   STATUS    RESTARTS   AGE
kyverno-admission-controller-xxxxx    1/1     Running   0          60s
kyverno-background-controller-xxxxx   1/1     Running   0          60s
kyverno-cleanup-controller-xxxxx      1/1     Running   0          60s
kyverno-reports-controller-xxxxx      1/1     Running   0          60s
```

### 3. Verify Webhooks are Registered

```bash
# Check ValidatingWebhookConfigurations
kubectl get validatingwebhookconfigurations | grep -E "gatekeeper|kyverno"

# Check MutatingWebhookConfigurations
kubectl get mutatingwebhookconfigurations | grep -E "gatekeeper|kyverno"
```

## Quick Installation Script

For convenience, use this one-liner:

```bash
# Install both policy engines
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.15.0/deploy/gatekeeper.yaml && \
kubectl apply -f https://github.com/kyverno/kyverno/releases/download/v1.11.0/install.yaml && \
echo "Waiting for policy engines to be ready..." && \
kubectl wait --for=condition=Ready pod -l control-plane=controller-manager -n gatekeeper-system --timeout=120s && \
kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=kyverno -n kyverno --timeout=120s && \
echo "✅ Policy engines installed successfully!"
```

## Post-Installation Verification

### Test Gatekeeper

```bash
# Apply a test ConstraintTemplate
cat <<EOF | kubectl apply -f -
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
EOF

# Verify it was created
kubectl get constrainttemplates
```

### Test Kyverno

```bash
# Apply a test ClusterPolicy
cat <<EOF | kubectl apply -f -
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-labels-test
spec:
  validationFailureAction: Audit
  background: true
  rules:
  - name: check-for-labels
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Label 'app' is required"
      pattern:
        metadata:
          labels:
            app: "?*"
EOF

# Verify it was created
kubectl get clusterpolicies
```

## Troubleshooting

### Gatekeeper pods not starting

```bash
# Check events
kubectl get events -n gatekeeper-system --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n gatekeeper-system -l control-plane=controller-manager
```

### Kyverno pods not starting

```bash
# Check events
kubectl get events -n kyverno --sort-by='.lastTimestamp'

# Check logs
kubectl logs -n kyverno -l app.kubernetes.io/name=kyverno
```

### Webhook not responding

```bash
# Check webhook configuration
kubectl get validatingwebhookconfigurations gatekeeper-validating-webhook-configuration -o yaml

# Test webhook connectivity
kubectl run test-pod --image=nginx --dry-run=server
```

## Uninstallation

If you need to remove the policy engines:

```bash
# Uninstall Kyverno
kubectl delete -f https://github.com/kyverno/kyverno/releases/download/v1.11.0/install.yaml

# Uninstall Gatekeeper
kubectl delete -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/v3.15.0/deploy/gatekeeper.yaml

# Clean up CRDs (WARNING: This will delete all policies)
kubectl delete crd -l gatekeeper.sh/system=yes
kubectl delete crd -l app.kubernetes.io/name=kyverno
```

## Next Steps

After installation, proceed to deploy the AI Agent governance policies:

1. **Pod Security Admission**: Update namespace labels
2. **Gatekeeper Policies**: Deploy ConstraintTemplates and Constraints
3. **Kyverno Policies**: Deploy ClusterPolicies

See `../01-gatekeeper/README.md` and `../03-kyverno/README.md` for details.

## Resources

- [Gatekeeper Documentation](https://open-policy-agent.github.io/gatekeeper/)
- [Kyverno Documentation](https://kyverno.io/docs/)
- [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
