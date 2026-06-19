# Hybrid Kubernetes Strategy: K3s vs. Managed K8s (EKS) Decision

This document details the selection criteria, load thresholds, configuration split, and cost projections for deploying the AI Agent Governance Framework in developer environments (K3s) vs. production environments (EKS).

## Comparison Summary Table

| KPI Dimension | K3s (Dev / Local Cluster) | Managed K8s / EKS (Production) |
| :--- | :--- | :--- |
| **Concurrent Agents** | < 50 agents | > 50 agents (auto-scales up to 500+) |
| **High Availability (HA)** | ❌ None (Single controller node acceptable) | ✅ Multi-AZ controller, HPA, and PDBs |
| **Secrets Engine** | CyberArk Conjur OSS (Self-hosted) | CyberArk Central Credential Provider / AWS Secrets Manager + IRSA |
| **CNI / NetworkPolicy** | flannel (L4-only default) | Calico (L4/L7 policy rules) |
| **LLM Gateway Endpoint** | Direct Public API (Gemini/Anthropic) | PrivateLink VPC Endpoint (AWS Bedrock us-gov-east-1) |
| **Ingress Controller** | Traefik (default K3s) | AWS ALB Ingress Controller |
| **Storage Class** | `local-path` (host path backed) | `gp3-encrypted` (KMS encrypted) |
| **Budget / Month** | < $200 / month | $2,000+ / month |
| **Compliance Readiness** | Dev / Testing only (Non-Compliant) | FedRAMP Moderate / DoD IL5 / NIST SP 800-207 |

---

## Load Thresholds and Sizing Rules

### Dev Sizing Profile (K3s)
* **Target Node Sizing:** 1x VM or Bare-Metal, 4 vCPUs, 8GiB RAM.
* **Storage Allocation:** 10GiB `local-path` volume allocation for short-term Redis checkpoints.
* **LLM Provider:** Direct REST connections over public endpoints to save VPC networking costs.

### Staging/Prod Sizing Profile (EKS)
* **Target Node Sizing:** 3x `m6i.xlarge` nodes (4 vCPUs, 16GiB RAM per node).
* **Storage Allocation:** gp3 volumes, minimum 100 IOPS, encrypted with AWS KMS CMK keys (SC-28).
* **Autoscaling (HPA):** Scales pods when CPU or Memory utilization exceeds 80%.

---

## Key Decision Matrix

1. **Deploy to K3s when:**
   * Developing and unit-testing policies or agent handlers.
   * Running local CI/CD checkouts.
   * Resource constraints apply (e.g. laptop or local server deployment).
   * Total token consumption is under 500K tokens per calendar day.

2. **Deploy to Managed K8s (EKS) when:**
   * Operating under FedRAMP Moderate compliance scope (NIST SP 800-53).
   * Requiring multi-region active-passive failover and recovery.
   * Multi-agent execution orchestrates database transactions or deployment changes.
   * Requiring mTLS inter-pod networking (using Istio or Linkerd) and Calico eBPF filtering.
