# 🧠 AI Agent Governance, Policy & Cost Framework

*Full content available in project artifacts*

This document defines the comprehensive **AI Governance and Policy Framework** for all agents operating within the `%project_name$` namespace.  
It ensures compliance, safety, accountability, and financial transparency across all AI-assisted automation.

---

## Key Sections
- **Agent Classification System (4 Tiers)** — defines autonomy, risk level, and oversight requirements.
- **Governance Framework** — outlines control boundaries, namespace management, and execution rules.
- **Policy Compliance** — maps to security, ethical, and compliance standards (e.g., NIST, DoD RMF, ISO 42001).
- **Cost Structure Framework** — defines token consumption models, API metering, and operational budgets.
- **Cost Tracking & Optimization** — details observability methods for cost/performance balancing.
- **Governance Controls** — includes auditability, escalation, and CI/CD enforcement.
- **Devcontainer Standards** — enforces vendor image patterns to reduce token waste and build time.

> 📂 *See full details in `/project-artifacts/governance/`.*

---

## 🧩 Governance Framework Overview

1. **Scope & Responsibility**
   - Agents must operate exclusively within the `%project_name$` namespace.
   - No cross-project actions or assumptions without human authorization.
   - All agent actions must be traceable, reproducible, and reversible.

2. **Accountability**
   - Each agent must declare its namespace, version, and role at startup.
   - Agents log all operations in structured, machine-readable formats (JSON or YAML).
   - Sensitive data must be masked in logs and never transmitted in plaintext.

3. **Cost Governance**
   - Agents must track compute and token consumption at task-level granularity.
   - Budget caps are defined per environment (e.g., `dev`, `test`, `prod`).
   - Exceeding thresholds triggers automated alerts and human escalation.
   - Agents should propose optimization or caching strategies before scaling horizontally.

4. **Policy Lifecycle**
   - All governance rules are version-controlled in the repository.
   - Agents must verify the active policy version before execution.
   - CI/CD pipelines validate compliance on every build or merge request.

---

## ⚖️ Policy Compliance Model

| Domain | Policy Objective | Enforcement Mechanism |
|--------|------------------|-----------------------|
| Security | Prevent unauthorized access, secret leaks, or privilege escalation | Namespace scoping, secret masking, approval gates |
| Compliance | Align with DoD RMF, NIST 800-53, ISO 42001 | Policy-as-code validation, audit-ready logs |
| Ethical | Maintain transparency, avoid bias or manipulation | Human-in-loop review, explainable outputs |
| Operational | Control cost, stability, and resource fairness | Token budgeting, dry-run enforcement |
| Governance | Ensure traceability and accountability | Signed logs, version-locking, CI/CD checks |

---

## 🧱 Policy Controls & Escalation Path

1. **Inspection-first**: All actions must start with read-only inspection.
2. **Confirmation-gated**: Destructive operations require explicit approval.
3. **Simulation Mode**: Default to dry-run for critical or resource-heavy operations.
4. **Escalation**: When scope or impact is ambiguous, escalate to human operator.

---

## 🛡️ AI Agent Governance Framework Guardrails

This section defines enforceable **guardrails** for all AI-driven agents, copilots, or automation services operating within the `%project_name$` namespace.  
It complements the general governance policy by introducing agent-specific safety, audit, and compliance controls.

> YAML Reference: `frameworks/agent-guardrail.yaml`

```yaml
version: 1.0
metadata:
  title: AI Agent Governance Framework Guardrails
  namespace: "%project_name$"
  updated: "2025-10-21"

scope:
  - Agents act strictly within project namespace.
  - Never create or modify external resources without authorization.
  - Always clarify scope ambiguity with human operator.

safety:
  - Suggest read-only inspection before modification.
  - Require confirmation before any destructive action.
  - All actions must be idempotent and reversible.
  - Default to dry-run for high-impact operations.

responsibility_separation:
  - build_time: Static dependencies and templates only.
  - runtime: Lightweight bootstrap only; no complex shell logic.
  - orchestration: Declare environment variables and ports in manifests.
  - application: Code-level customization preferred over shell wrappers.
  - governance: CI/CD enforces and rejects violations.

file_system:
  - Operate only within `~/projects/%project_name$` (Linux/WSL).
  - Confirm before overwriting or deleting existing files.
  - Explicitly identify symlink sources and targets.
  - Default to Linux filesystem for heavy workloads.

memory_state:
  - Do not assume persistent memory; re-establish context each session.
  - Treat only container volumes or defined storage as persistence layers.
  - Clarify ephemeral vs persistent changes.

audit_trace:
  - Log every action in structured JSON.
  - Include timestamp, namespace, justification, and outcome.
  - Mask sensitive values in logs.

secrets_management:
  - Never expose secrets in outputs or logs.
  - Retrieve secrets only from approved secret stores.

policy_versioning:
  - Agents verify current policy version at startup.
  - Refuse execution if policy is outdated.

human_escalation:
  - Stop and escalate when encountering ambiguous or destructive tasks.

resource_governance:
  - Respect CPU, memory, disk, and API quotas.
  - Never exceed limits without explicit override.

cross_agent_comm:
  - Use structured, schema-validated messages.
  - Reject malformed or ambiguous communication.

ci_cd_enforcement:
  - Reject builds violating guardrail rules.
  - Require idempotency, explicit env vars, and reproducible builds.
  - Lint and block merges on policy violations.

devcontainer_standards:
  - Use existing vendor images instead of custom Dockerfiles.
  - Pin images by SHA256 digest for reproducibility.
  - Mount specifications as read-only to prevent modification.
  - Prefer devcontainer features over custom build steps.
  - Track and report token savings from vendor image usage.

---

## 🐳 Devcontainer Vendor Image Standards

To minimize token waste and build time overhead, all projects MUST follow the **Devcontainer Vendor Image Workflow Pattern** when configuring development containers.

### Requirements

1. **Use Vendor Images**: Prefer existing, trusted images from:
   - Microsoft Container Registry (`mcr.microsoft.com/devcontainers/*`)
   - GitHub Container Registry (`ghcr.io/*`)
   - Vendor-specific tools (`openapitools/*`, `bufbuild/*`, etc.)

2. **Pin by Digest**: Always pin images using SHA256 digest:
   ```json
   "image": "mcr.microsoft.com/devcontainers/python:3.11@sha256:abc123..."
   ```

3. **Avoid Custom Builds**: Do not use `"build": { "dockerfile": "Dockerfile" }` unless justified.
   - Custom builds add 6-10 minutes per rebuild
   - Custom builds consume ~400+ tokens per rebuild vs ~15 tokens for pulls
   - Requires written justification and approval

4. **Use Features**: Add tools via devcontainer features, not custom Dockerfiles:
   ```json
   "features": {
     "ghcr.io/devcontainers/features/github-cli:1": {},
     "ghcr.io/devcontainers/features/docker-in-docker:2": {}
   }
   ```

### Token Impact

| Approach | Tokens per Rebuild | Time per Rebuild | Annual Savings (100 rebuilds) |
|----------|-------------------|------------------|-------------------------------|
| Custom Dockerfile | ~425 tokens | 8-12 minutes | 41,000 tokens = $410 |
| Vendor Image | ~15 tokens | 1-3 minutes | 0 tokens (baseline) |
| **Savings** | **96%** | **~85%** | **$410/year per developer** |

### Documentation & Tools

- **Workflow Guide**: [docs/DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md](DEVCONTAINER-VENDOR-IMAGE-WORKFLOW.md)
- **Governance Integration**: [docs/DEVCONTAINER-GOVERNANCE-INTEGRATION.md](DEVCONTAINER-GOVERNANCE-INTEGRATION.md)
- **Templates**: `templates/.devcontainer/`
- **Helper Script**: `scripts/get-image-digest.sh <image:tag>`

### Enforcement

1. **Pre-commit hook**: Validates devcontainer configuration
2. **CI/CD check**: Blocks PRs with non-compliant devcontainers
3. **Project creation**: Automated templates use vendor images by default
4. **Quarterly audit**: Reviews compliance and calculates token savings

See [DEVCONTAINER-GOVERNANCE-INTEGRATION.md](DEVCONTAINER-GOVERNANCE-INTEGRATION.md) for full enforcement mechanisms.

---

Document Version
Version: 1.0
Status: Active
Maintainer: Governance Working Group
Last Updated: 2025-10-21
Next Review: 2026-04-01
