# CyberArk Conjur Secretless Brokerage Integration

This document outlines the architecture, data flow, and configuration requirements for implementing secretless brokerage using CyberArk Conjur Open Source (or centralized AWS Secrets Manager with IRSA) within the AI Agent Governance Framework.

## Overview

Static Kubernetes secrets are prohibited in production environments (FedRAMP Moderate / NIST IA-5). Instead of mounting static credentials in agent pods, agents request dynamic, short-lived tokens from CyberArk Conjur. 

The **Secretless Brokerage Pattern** projects Kubernetes ServiceAccount tokens into the pods, which Conjur validates using the Kubernetes TokenReview API to issue ephemeral secrets.

## Architecture Data Flow

```
+--------------------------------------------------------------------------+
| Kubernetes Pod (Namespace: ai-agents-prod)                              |
|                                                                          |
|  +-------------------+               +-------------------------------+   |
|  |                   |  (2) Token    |                               |   |
|  |  GovernanceRouter | <-----------  | Projected Token Volume        |   |
|  |  (PE Engine / Go) |               | /var/run/secrets/conjur/token |   |
|  |                   |               +-------------------------------+   |
|  +-------------------+                                                   |
|          |                                                               |
|          | (3) Authenticate with K8s Projected Token                     |
|          v                                                               |
|  +-------------------+                                                   |
|  | Conjur Sidecar    |                                                   |
|  | (conjur-authn)    |                                                   |
|  +-------------------+                                                   |
+----------|---------------------------------------------------------------+
           |
           | (4) TokenReview Request (Validate Pod Identity)
           v
+------------------------+           +------------------------+
| K8s API Server         | <-------> | CyberArk Conjur Server |
| (authentication.k8s.io)|           | (authn-k8s service)    |
+------------------------+           +------------------------+
                                                 |
                                                 | (5) Issue Conjur Session Token
                                                 v
                                     +------------------------+
                                     | Conjur Client Sidecar  |
                                     | (Writes local session) |
                                     +------------------------+
```

## Step-by-Step Lifecycle

1. **ServiceAccount Token Projection:**
   The agent's Pod spec defines an explicit projected volume mapping the Kubernetes ServiceAccount token with a short expiration (900 seconds) and specific audience (`conjur`).
2. **Conjur Authentication:**
   The `conjur-authn` sidecar client reads the projected token and posts it to the Conjur authenticator endpoint (`/authn-k8s/{service_account}/authenticate`).
3. **Identity Attestation:**
   The Conjur server performs a `TokenReview` request to the Kubernetes API server, verifying that the token is valid, hasn't expired, and belongs to the designated ServiceAccount, namespace, and image signature.
4. **Session Token Issuance:**
   Upon successful verification, Conjur returns a short-lived Conjur session token (valid for 15 minutes).
5. **Secure Checkout Broker (GovernanceRouter):**
   The `GovernanceRouter` checks out the target secret (e.g. LLM API Key) using the Conjur session token.
   * **In-Memory ONLY:** Secrets are kept in-memory inside the `GovernanceRouter` process. They are NEVER written to the local filesystem or environment variables.
6. **Revocation / Check-In on Pause:**
   When an agent transitions to a `SUSPENDED` state (waiting for human Jira CR approval), the `GovernanceRouter` explicitly revokes the session by making a `DELETE` request to the Conjur session endpoint, minimizing idle credential exposure.

## Kubernetes Configuration Example

### ServiceAccount (`templates/serviceaccount.yaml`)
To prevent default token leakage, ServiceAccounts explicitly set `automountServiceAccountToken: false`.
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: security-agent
  namespace: ai-agents-prod
automountServiceAccountToken: false
```

### Projected Volume (`templates/deployment.yaml`)
The token is projected via a dedicated memory-backed volume:
```yaml
volumes:
  - name: conjur-token
    projected:
      sources:
        - serviceAccountToken:
            path: token
            expirationSeconds: 900
            audience: conjur
```

## Conjur Access Policy Example (`conjur_policy.hcl`)
Policy definition mapping the Kubernetes ServiceAccount identities to safe secrets paths:
```hcl
- !policy
  id: k8s-agents
  body:
    - !group clients
    
    - !host ai-agents-prod/security-agent
      annotations:
        authn-k8s/namespace: ai-agents-prod
        authn-k8s/service-account: security-agent
        
    - !host ai-agents-prod/it-ops-agent
      annotations:
        authn-k8s/namespace: ai-agents-prod
        authn-k8s/service-account: it-ops-agent

    - !grant
      role: !group clients
      member: !host ai-agents-prod/security-agent

    - !privilege
      resource: !variable secrets/llm-api-key
      action: [ read ]
      role: !group clients
```
